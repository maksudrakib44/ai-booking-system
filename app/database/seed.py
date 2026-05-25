import asyncio
import random
from datetime import datetime, timedelta
from app.database.models import Base, BusRoute
from app.database.session import engine, AsyncSessionLocal
from sqlalchemy import select

# Base schedules – each dict describes one service (price, operator, times, etc.)
BASE_ROUTES = [
    # Dhaka ↔ Sylhet
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Sylhet",
     "dep_time":"08:00","arr_time":"15:00","price":950,"ac":True,"total_seats":40},
    {"operator":"Green Line","source":"Dhaka","destination":"Sylhet",
     "dep_time":"07:30","arr_time":"13:30","price":1350,"ac":True,"total_seats":36},
    {"operator":"Ena Transport","source":"Dhaka","destination":"Sylhet",
     "dep_time":"10:00","arr_time":"17:00","price":800,"ac":False,"total_seats":44},
    {"operator":"Hanif Enterprise","source":"Dhaka","destination":"Sylhet",
     "dep_time":"11:00","arr_time":"18:00","price":900,"ac":False,"total_seats":44},
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Sylhet",
     "dep_time":"23:00","arr_time":"05:00+1","price":950,"ac":True,"total_seats":40},
    # Dhaka ↔ Chittagong
    {"operator":"Soudia","source":"Dhaka","destination":"Chittagong",
     "dep_time":"09:00","arr_time":"16:00","price":850,"ac":True,"total_seats":40},
    {"operator":"TR Travels","source":"Dhaka","destination":"Chittagong",
     "dep_time":"10:30","arr_time":"17:30","price":750,"ac":False,"total_seats":48},
    {"operator":"Green Line","source":"Dhaka","destination":"Chittagong",
     "dep_time":"08:00","arr_time":"14:30","price":1200,"ac":True,"total_seats":36},
    {"operator":"Shyamoli Paribahan","source":"Dhaka","destination":"Chittagong",
     "dep_time":"22:00","arr_time":"05:00+1","price":700,"ac":False,"total_seats":52},
    # Dhaka ↔ Cox’s Bazar
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Cox's Bazar",
     "dep_time":"22:00","arr_time":"08:00+1","price":1200,"ac":True,"total_seats":36},
    {"operator":"Green Line","source":"Dhaka","destination":"Cox's Bazar",
     "dep_time":"21:30","arr_time":"07:30+1","price":1500,"ac":True,"total_seats":36},
    {"operator":"Saintmartin Paribahan","source":"Dhaka","destination":"Cox's Bazar",
     "dep_time":"20:00","arr_time":"06:00+1","price":1000,"ac":False,"total_seats":40},
    # Dhaka ↔ Rajshahi
    {"operator":"Hanif Enterprise","source":"Dhaka","destination":"Rajshahi",
     "dep_time":"06:00","arr_time":"12:00","price":1100,"ac":True,"total_seats":36},
    {"operator":"National Travels","source":"Dhaka","destination":"Rajshahi",
     "dep_time":"07:30","arr_time":"13:30","price":900,"ac":False,"total_seats":44},
    # Dhaka ↔ Khulna
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Khulna",
     "dep_time":"08:00","arr_time":"14:00","price":1000,"ac":True,"total_seats":40},
    {"operator":"Soudia","source":"Dhaka","destination":"Khulna",
     "dep_time":"10:00","arr_time":"17:00","price":800,"ac":False,"total_seats":44},
    # Dhaka ↔ Comilla
    {"operator":"TR Travels","source":"Dhaka","destination":"Comilla",
     "dep_time":"09:00","arr_time":"11:00","price":400,"ac":False,"total_seats":48},
    {"operator":"Green Line","source":"Dhaka","destination":"Comilla",
     "dep_time":"10:30","arr_time":"12:30","price":550,"ac":True,"total_seats":36},
    # Dhaka ↔ Barisal
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Barisal",
     "dep_time":"06:00","arr_time":"12:00","price":900,"ac":True,"total_seats":36},
    {"operator":"Hanif Enterprise","source":"Dhaka","destination":"Barisal",
     "dep_time":"08:00","arr_time":"14:00","price":700,"ac":False,"total_seats":44},
    # Dhaka ↔ Kishoreganj
    {"operator":"Anondo Paribahan","source":"Dhaka","destination":"Kishoreganj",
     "dep_time":"07:00","arr_time":"10:00","price":350,"ac":False,"total_seats":40},
    {"operator":"BRTC","source":"Dhaka","destination":"Kishoreganj",
     "dep_time":"11:00","arr_time":"14:00","price":300,"ac":False,"total_seats":52},
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Kishoreganj",
     "dep_time":"15:00","arr_time":"18:00","price":450,"ac":True,"total_seats":36},
    # Dhaka ↔ Chandpur
    {"operator":"Meghna Express","source":"Dhaka","destination":"Chandpur",
     "dep_time":"08:00","arr_time":"13:00","price":500,"ac":False,"total_seats":44},
    {"operator":"Padma Express","source":"Dhaka","destination":"Chandpur",
     "dep_time":"13:00","arr_time":"18:00","price":600,"ac":True,"total_seats":36},
    # Dhaka ↔ Mymensingh
    {"operator":"Ena Transport","source":"Dhaka","destination":"Mymensingh",
     "dep_time":"09:00","arr_time":"12:00","price":400,"ac":False,"total_seats":44},
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Mymensingh",
     "dep_time":"11:00","arr_time":"14:00","price":550,"ac":True,"total_seats":36},
    # Dhaka ↔ Rangpur
    {"operator":"Hanif Enterprise","source":"Dhaka","destination":"Rangpur",
     "dep_time":"08:00","arr_time":"14:00","price":1000,"ac":True,"total_seats":40},
    {"operator":"National Travels","source":"Dhaka","destination":"Rangpur",
     "dep_time":"22:00","arr_time":"04:00+1","price":800,"ac":False,"total_seats":48},
    # Dhaka ↔ Bogra
    {"operator":"Shyamoli Paribahan","source":"Dhaka","destination":"Bogra",
     "dep_time":"07:00","arr_time":"12:00","price":700,"ac":False,"total_seats":44},
    {"operator":"Green Line","source":"Dhaka","destination":"Bogra",
     "dep_time":"10:00","arr_time":"15:00","price":900,"ac":True,"total_seats":36},
    # Dhaka ↔ Jessore
    {"operator":"Shohag Paribahan","source":"Dhaka","destination":"Jessore",
     "dep_time":"09:00","arr_time":"15:00","price":1100,"ac":True,"total_seats":40},
    {"operator":"Soudia","source":"Dhaka","destination":"Jessore",
     "dep_time":"23:00","arr_time":"05:00+1","price":850,"ac":False,"total_seats":44},
    # Inter‑city (non‑Dhaka)
    {"operator":"Ena Transport","source":"Sylhet","destination":"Chittagong",
     "dep_time":"07:00","arr_time":"15:00","price":1200,"ac":False,"total_seats":44},
    {"operator":"Green Line","source":"Chittagong","destination":"Cox's Bazar",
     "dep_time":"08:00","arr_time":"11:30","price":600,"ac":True,"total_seats":36},
    {"operator":"Hanif Enterprise","source":"Rajshahi","destination":"Khulna",
     "dep_time":"10:00","arr_time":"17:00","price":950,"ac":False,"total_seats":44},
    {"operator":"Local Express","source":"Kishoreganj","destination":"Chandpur",
     "dep_time":"06:00","arr_time":"10:00","price":450,"ac":False,"total_seats":40},
]

def generate_schedules():
    """Create BusRoute objects for the next 7 days, with unique IDs and random availability."""
    today = datetime.now().date()
    bus_objects = []
    global_id = 1

    for day_offset in range(7):          # 0 = today, 1 = tomorrow, … 6
        date = today + timedelta(days=day_offset)
        for route in BASE_ROUTES:
            dep_h, dep_m = map(int, route["dep_time"].split(":"))
            arr_raw = route["arr_time"]
            # Handle "+1" suffix (next day arrival)
            next_day = False
            if "+1" in arr_raw:
                next_day = True
                arr_raw = arr_raw.replace("+1", "")
            arr_h, arr_m = map(int, arr_raw.split(":"))

            dep_dt = datetime(date.year, date.month, date.day, dep_h, dep_m)
            arr_dt = datetime(date.year, date.month, date.day, arr_h, arr_m)
            if next_day:
                arr_dt += timedelta(days=1)

            # simulate random bookings: available seats = 70‑100% of total
            avail = random.randint(int(route["total_seats"] * 0.7), route["total_seats"])

            bus_id = f"BUS-{global_id:04d}"      # simple unique ID
            bus_objects.append(BusRoute(
                id=bus_id,
                operator=route["operator"],
                source=route["source"],
                destination=route["destination"],
                departure_time=dep_dt,
                arrival_time=arr_dt,
                price=route["price"],
                ac=route["ac"],
                total_seats=route["total_seats"],
                available_seats=avail
            ))
            global_id += 1

    return bus_objects

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        # check if already seeded
        existing = (await session.execute(select(BusRoute))).scalars().first()
        if existing:
            print("Database already seeded. Delete travel_ai.db first.")
            return
        buses = generate_schedules()
        session.add_all(buses)
        await session.commit()
        print(f"Seeded {len(buses)} buses across 7 days.")

if __name__ == "__main__":
    asyncio.run(seed())