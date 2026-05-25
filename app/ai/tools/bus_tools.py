from langchain_core.tools import tool
from sqlalchemy import select, func
from datetime import datetime, timedelta, date
from app.database.session import AsyncSessionLocal
from app.database.models import BusRoute, Booking, User
from app.services.redis_service import get_cached_routes, cache_routes
import re
import pytz

DHAKA = pytz.timezone("Asia/Dhaka")

def now_dhaka():
    """Current datetime in Dhaka (naive, to match DB times)."""
    return datetime.now(DHAKA).replace(tzinfo=None)

def parse_relative_date(text: str) -> str | None:
    """Convert relative date strings to YYYY-MM-DD. Returns None if unrecognised."""
    text = text.strip().lower()
    today = now_dhaka().date()
    if text in ("today", "now"):
        return today.isoformat()
    if text in ("tomorrow", "tomorow"):
        return (today + timedelta(days=1)).isoformat()
    if text in ("day after tomorrow", "overmorrow"):
        return (today + timedelta(days=2)).isoformat()
    weekdays = ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"]
    for i, day in enumerate(weekdays):
        if text.startswith("next ") and day in text:
            days_ahead = (i - today.weekday()) % 7
            if days_ahead <= 0:
                days_ahead += 7
            return (today + timedelta(days=days_ahead)).isoformat()
    if re.match(r"^\d{4}-\d{2}-\d{2}$", text):
        try:
            datetime.strptime(text, "%Y-%m-%d")
            return text
        except ValueError:
            pass
    return None

@tool
async def search_bus_routes(source: str, destination: str, date: str = None) -> str:
    """
    Search available buses between two cities.
    - Optional 'date': 'today', 'tomorrow', 'YYYY-MM-DD', 'next 7 days', etc.
    - When 'today', only future departures are shown.
    """
    now = now_dhaka()
    today = now.date()

    # Determine date range filter
    if date:
        if "next 7 days" in date.lower() or "within 7 days" in date.lower():
            start_date = today.isoformat()
            end_date = (today + timedelta(days=6)).isoformat()
        else:
            parsed = parse_relative_date(date)
            if parsed:
                start_date = parsed
                end_date = parsed     # single day
            else:
                start_date = end_date = None   # fallback: no date filter
    else:
        # No date given: only future buses (from now onwards)
        start_date = today.isoformat()
        end_date = None

    # Build cache key
    cache_key = f"routes:{source.lower()}:{destination.lower()}:{start_date}:{end_date}"

    cached = await get_cached_routes(cache_key)
    if cached:
        return cached + " [cached]"

    async with AsyncSessionLocal() as session:
        query = select(BusRoute).where(
            BusRoute.source.ilike(source),
            BusRoute.destination.ilike(destination)
        )

        if start_date:
            if end_date and end_date != start_date:
                query = query.where(
                    func.date(BusRoute.departure_time) >= start_date,
                    func.date(BusRoute.departure_time) <= end_date
                )
            else:
                query = query.where(func.date(BusRoute.departure_time) == start_date)

        result = await session.execute(query)
        buses = result.scalars().all()

        # For "today" (or no date), hide already departed buses
        if (date and start_date == today.isoformat()) or not date:
            buses = [b for b in buses if b.departure_time > now]

        if not buses:
            msg = f"No buses found from {source} to {destination}"
            if date:
                msg += f" on {date}"
            return msg

        lines = []
        for b in buses:
            lines.append(
                f"ID: {b.id} | {b.operator} | {b.departure_time.strftime('%Y-%m-%d %H:%M')} → "
                f"{b.arrival_time.strftime('%Y-%m-%d %H:%M')} | Price: {b.price} BDT | "
                f"{'AC' if b.ac else 'Non-AC'} | Seats: {b.available_seats}"
            )
        result_str = "\n".join(lines)
        await cache_routes(cache_key, result_str)
        return result_str

@tool
async def check_seat_availability(bus_id: str) -> str:
    """Return current seat count and details for a specific bus (date‑sensitive)."""
    async with AsyncSessionLocal() as session:
        bus = await session.get(BusRoute, bus_id)
        if not bus:
            return f"Bus with ID {bus_id} not found."
        return (
            f"Bus {bus.id} ({bus.operator}): {bus.available_seats} seats available out of {bus.total_seats}. "
            f"{'AC' if bus.ac else 'Non-AC'} | Price: {bus.price} BDT | "
            f"Departure: {bus.departure_time.strftime('%Y-%m-%d %H:%M')} | "
            f"Arrival: {bus.arrival_time.strftime('%Y-%m-%d %H:%M')}"
        )

@tool
async def book_ticket(user_id: str, bus_id: str, seat_count: int, seat_preference: str = "") -> str:
    """
    Book a number of seats on a specific bus.
    
    Optional seat_preference can be:
      - "not first row"       (avoid row 1)
      - "window"              (A or D seats, where rows have A,B,C,D)
      - "aisle"               (B or C seats)
      - any other custom string (the tool will try its best)
    If no preference is given, seats are assigned arbitrarily.
    
    Returns a confirmation message or error description.
    """
    async with AsyncSessionLocal() as session:
        bus = await session.get(BusRoute, bus_id)
        if not bus:
            return f"Bus ID {bus_id} not found."
        if seat_count > bus.available_seats:
            return f"Not enough seats: only {bus.available_seats} left, you requested {seat_count}."

        # Generate a simple seat map (rows of 4 seats A-D)
        rows = bus.total_seats // 4
        seat_labels = []
        for row in range(1, rows + 1):
            for col in ['A', 'B', 'C', 'D']:
                seat_labels.append(f"{row}{col}")

        # Filter by preference
        filtered = []
        preference = seat_preference.lower().strip()
        for seat in seat_labels:
            # Skip first row if requested
            if "not first row" in preference and seat.startswith("1"):
                continue
            # Window preference
            if "window" in preference and not (seat.endswith("A") or seat.endswith("D")):
                continue
            # Aisle preference
            if "aisle" in preference and not (seat.endswith("B") or seat.endswith("C")):
                continue
            filtered.append(seat)

        # If filtered list is shorter than needed, return error
        if len(filtered) < seat_count:
            return f"Not enough seats matching '{seat_preference}': only {len(filtered)} suitable seats available."

        # Pick the first seat_count seats from the filtered list (real system would pick randomly)
        chosen = filtered[:seat_count]

        # Deduct seats
        bus.available_seats -= seat_count

        # Create booking
        user = None
        if user_id and user_id != "anonymous" and user_id.isdigit():
            user = await session.get(User, int(user_id))

        booking = Booking(
            user_id=user.id if user else None,
            bus_id=bus_id,
            seat_numbers=chosen,
            total_price=bus.price * seat_count,
            status="confirmed"
        )
        session.add(booking)
        await session.commit()

        return (
            f"Booking confirmed! ID: {booking.id} | {bus.operator} | "
            f"Seats: {', '.join(booking.seat_numbers)} | Total: {booking.total_price} BDT | "
            f"Departure: {bus.departure_time.strftime('%Y-%m-%d %H:%M')}"
        )