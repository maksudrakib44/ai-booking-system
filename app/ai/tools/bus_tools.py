from langchain_core.tools import tool
from sqlalchemy import select
from datetime import timedelta
from app.database.session import AsyncSessionLocal
from app.database.models import BusRoute, Booking, User
from app.services.redis_service import get_cached_routes, cache_routes

@tool
async def search_bus_routes(source: str, destination: str) -> str:
    """
    Search available buses between two cities. Returns ALL buses for that route.
    Use the departure times in the result to filter by date if needed.
    """
    cached = await get_cached_routes(source, destination)
    if cached:
        return cached + " [cached]"

    async with AsyncSessionLocal() as session:
        query = select(BusRoute).where(
            BusRoute.source.ilike(source),
            BusRoute.destination.ilike(destination)
        )
        result = await session.execute(query)
        buses = result.scalars().all()
        if not buses:
            return f"No buses found from {source} to {destination}."
        lines = []
        for b in buses:
            lines.append(
                f"ID: {b.id} | {b.operator} | {b.departure_time.strftime('%Y-%m-%d %H:%M')} → "
                f"{b.arrival_time.strftime('%Y-%m-%d %H:%M')} | Price: {b.price} BDT | "
                f"{'AC' if b.ac else 'Non-AC'} | Seats: {b.available_seats}"
            )
        result_str = "\n".join(lines)
        await cache_routes(source, destination, result_str)
        return result_str

@tool
async def check_seat_availability(bus_id: str) -> str:
    """
    Return available seats count and details for a bus.
    """
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
async def book_ticket(user_id: str, bus_id: str, seat_count: int) -> str:
    """
    Book a number of seats for a user on a specific bus.
    Returns a confirmation message or error description.
    """
    async with AsyncSessionLocal() as session:
        bus = await session.get(BusRoute, bus_id)
        if not bus:
            return f"Bus ID {bus_id} not found."
        if seat_count > bus.available_seats:
            return f"Not enough seats: only {bus.available_seats} left, you requested {seat_count}."

        user = None
        if user_id and user_id != "anonymous" and user_id.isdigit():
            user = await session.get(User, int(user_id))

        booking = Booking(
            user_id=user.id if user else None,
            bus_id=bus_id,
            seat_numbers=[f"{bus.id}-{i+1}" for i in range(seat_count)],
            total_price=bus.price * seat_count,
            status="confirmed"
        )
        bus.available_seats -= seat_count
        session.add(booking)
        await session.commit()
        return (
            f"Booking confirmed! ID: {booking.id} | {bus.operator} | "
            f"Seats: {', '.join(booking.seat_numbers)} | Total: {booking.total_price} BDT | "
            f"Departure: {bus.departure_time.strftime('%Y-%m-%d %H:%M')}"
        )