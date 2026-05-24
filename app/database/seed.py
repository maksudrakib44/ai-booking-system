import asyncio
from datetime import datetime
from app.database.models import Base, BusRoute
from app.database.session import engine, AsyncSessionLocal
from sqlalchemy import select

BUS_SEED_DATA = [
    # ========== Original 37 routes (forward) ==========
    # Dhaka ↔ Sylhet
    {"id":"B1","operator":"Shohag Paribahan","source":"Dhaka","destination":"Sylhet",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":950,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"B2","operator":"Green Line","source":"Dhaka","destination":"Sylhet",
     "departure_time":datetime(2026,5,25,7,30),"arrival_time":datetime(2026,5,25,13,30),
     "price":1350,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B3","operator":"Ena Transport","source":"Dhaka","destination":"Sylhet",
     "departure_time":datetime(2026,5,25,10,0),"arrival_time":datetime(2026,5,25,17,0),
     "price":800,"ac":False,"total_seats":44,"available_seats":44},
    {"id":"B4","operator":"Hanif Enterprise","source":"Dhaka","destination":"Sylhet",
     "departure_time":datetime(2026,5,25,11,0),"arrival_time":datetime(2026,5,25,18,0),
     "price":900,"ac":False,"total_seats":44,"available_seats":44},
    {"id":"B5","operator":"Shohag Paribahan","source":"Dhaka","destination":"Sylhet",
     "departure_time":datetime(2026,5,25,23,0),"arrival_time":datetime(2026,5,26,5,0),
     "price":950,"ac":True,"total_seats":40,"available_seats":40},

    # Dhaka ↔ Chittagong
    {"id":"B6","operator":"Soudia","source":"Dhaka","destination":"Chittagong",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,16,0),
     "price":850,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"B7","operator":"TR Travels","source":"Dhaka","destination":"Chittagong",
     "departure_time":datetime(2026,5,25,10,30),"arrival_time":datetime(2026,5,25,17,30),
     "price":750,"ac":False,"total_seats":48,"available_seats":48},
    {"id":"B8","operator":"Green Line","source":"Dhaka","destination":"Chittagong",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,14,30),
     "price":1200,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B9","operator":"Shyamoli Paribahan","source":"Dhaka","destination":"Chittagong",
     "departure_time":datetime(2026,5,25,22,0),"arrival_time":datetime(2026,5,26,5,0),
     "price":700,"ac":False,"total_seats":52,"available_seats":52},

    # Dhaka ↔ Cox’s Bazar
    {"id":"B10","operator":"Shohag Paribahan","source":"Dhaka","destination":"Cox's Bazar",
     "departure_time":datetime(2026,5,25,22,0),"arrival_time":datetime(2026,5,26,8,0),
     "price":1200,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B11","operator":"Green Line","source":"Dhaka","destination":"Cox's Bazar",
     "departure_time":datetime(2026,5,25,21,30),"arrival_time":datetime(2026,5,26,7,30),
     "price":1500,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B12","operator":"Saintmartin Paribahan","source":"Dhaka","destination":"Cox's Bazar",
     "departure_time":datetime(2026,5,25,20,0),"arrival_time":datetime(2026,5,26,6,0),
     "price":1000,"ac":False,"total_seats":40,"available_seats":40},

    # Dhaka ↔ Rajshahi
    {"id":"B13","operator":"Hanif Enterprise","source":"Dhaka","destination":"Rajshahi",
     "departure_time":datetime(2026,5,25,6,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":1100,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B14","operator":"National Travels","source":"Dhaka","destination":"Rajshahi",
     "departure_time":datetime(2026,5,25,7,30),"arrival_time":datetime(2026,5,25,13,30),
     "price":900,"ac":False,"total_seats":44,"available_seats":44},

    # Dhaka ↔ Khulna
    {"id":"B15","operator":"Shohag Paribahan","source":"Dhaka","destination":"Khulna",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":1000,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"B16","operator":"Soudia","source":"Dhaka","destination":"Khulna",
     "departure_time":datetime(2026,5,25,10,0),"arrival_time":datetime(2026,5,25,17,0),
     "price":800,"ac":False,"total_seats":44,"available_seats":44},

    # Dhaka ↔ Comilla
    {"id":"B17","operator":"TR Travels","source":"Dhaka","destination":"Comilla",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,11,0),
     "price":400,"ac":False,"total_seats":48,"available_seats":48},
    {"id":"B18","operator":"Green Line","source":"Dhaka","destination":"Comilla",
     "departure_time":datetime(2026,5,25,10,30),"arrival_time":datetime(2026,5,25,12,30),
     "price":550,"ac":True,"total_seats":36,"available_seats":36},

    # Dhaka ↔ Barisal
    {"id":"B19","operator":"Shohag Paribahan","source":"Dhaka","destination":"Barisal",
     "departure_time":datetime(2026,5,25,6,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":900,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B20","operator":"Hanif Enterprise","source":"Dhaka","destination":"Barisal",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":700,"ac":False,"total_seats":44,"available_seats":44},

    # Dhaka ↔ Kishoreganj
    {"id":"B21","operator":"Anondo Paribahan","source":"Dhaka","destination":"Kishoreganj",
     "departure_time":datetime(2026,5,25,7,0),"arrival_time":datetime(2026,5,25,10,0),
     "price":350,"ac":False,"total_seats":40,"available_seats":40},
    {"id":"B22","operator":"BRTC","source":"Dhaka","destination":"Kishoreganj",
     "departure_time":datetime(2026,5,25,11,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":300,"ac":False,"total_seats":52,"available_seats":52},
    {"id":"B23","operator":"Shohag Paribahan","source":"Dhaka","destination":"Kishoreganj",
     "departure_time":datetime(2026,5,25,15,0),"arrival_time":datetime(2026,5,25,18,0),
     "price":450,"ac":True,"total_seats":36,"available_seats":36},

    # Dhaka ↔ Chandpur
    {"id":"B24","operator":"Meghna Express","source":"Dhaka","destination":"Chandpur",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,13,0),
     "price":500,"ac":False,"total_seats":44,"available_seats":44},
    {"id":"B25","operator":"Padma Express","source":"Dhaka","destination":"Chandpur",
     "departure_time":datetime(2026,5,25,13,0),"arrival_time":datetime(2026,5,25,18,0),
     "price":600,"ac":True,"total_seats":36,"available_seats":36},

    # Dhaka ↔ Mymensingh
    {"id":"B26","operator":"Ena Transport","source":"Dhaka","destination":"Mymensingh",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":400,"ac":False,"total_seats":44,"available_seats":44},
    {"id":"B27","operator":"Shohag Paribahan","source":"Dhaka","destination":"Mymensingh",
     "departure_time":datetime(2026,5,25,11,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":550,"ac":True,"total_seats":36,"available_seats":36},

    # Dhaka ↔ Rangpur
    {"id":"B28","operator":"Hanif Enterprise","source":"Dhaka","destination":"Rangpur",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":1000,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"B29","operator":"National Travels","source":"Dhaka","destination":"Rangpur",
     "departure_time":datetime(2026,5,25,22,0),"arrival_time":datetime(2026,5,26,4,0),
     "price":800,"ac":False,"total_seats":48,"available_seats":48},

    # Dhaka ↔ Bogra
    {"id":"B30","operator":"Shyamoli Paribahan","source":"Dhaka","destination":"Bogra",
     "departure_time":datetime(2026,5,25,7,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":700,"ac":False,"total_seats":44,"available_seats":44},
    {"id":"B31","operator":"Green Line","source":"Dhaka","destination":"Bogra",
     "departure_time":datetime(2026,5,25,10,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":900,"ac":True,"total_seats":36,"available_seats":36},

    # Dhaka ↔ Jessore
    {"id":"B32","operator":"Shohag Paribahan","source":"Dhaka","destination":"Jessore",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":1100,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"B33","operator":"Soudia","source":"Dhaka","destination":"Jessore",
     "departure_time":datetime(2026,5,25,23,0),"arrival_time":datetime(2026,5,26,5,0),
     "price":850,"ac":False,"total_seats":44,"available_seats":44},

    # Inter‑city (non‑Dhaka)
    {"id":"B34","operator":"Ena Transport","source":"Sylhet","destination":"Chittagong",
     "departure_time":datetime(2026,5,25,7,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":1200,"ac":False,"total_seats":44,"available_seats":44},
    {"id":"B35","operator":"Green Line","source":"Chittagong","destination":"Cox's Bazar",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,11,30),
     "price":600,"ac":True,"total_seats":36,"available_seats":36},
    {"id":"B36","operator":"Hanif Enterprise","source":"Rajshahi","destination":"Khulna",
     "departure_time":datetime(2026,5,25,10,0),"arrival_time":datetime(2026,5,25,17,0),
     "price":950,"ac":False,"total_seats":44,"available_seats":44},

    # Kishoreganj ↔ Chandpur (already present)
    {"id":"B37","operator":"Local Express","source":"Kishoreganj","destination":"Chandpur",
     "departure_time":datetime(2026,5,25,6,0),"arrival_time":datetime(2026,5,25,10,0),
     "price":450,"ac":False,"total_seats":40,"available_seats":40},

    # ========== REVERSE ROUTES ==========
    # Sylhet → Dhaka
    {"id":"R1","operator":"Shohag Paribahan","source":"Sylhet","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":950,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"R2","operator":"Green Line","source":"Sylhet","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,7,30),"arrival_time":datetime(2026,5,25,13,30),
     "price":1350,"ac":True,"total_seats":36,"available_seats":36},
    # Chittagong → Dhaka
    {"id":"R3","operator":"Soudia","source":"Chittagong","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,16,0),
     "price":850,"ac":True,"total_seats":40,"available_seats":40},
    {"id":"R4","operator":"TR Travels","source":"Chittagong","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,10,30),"arrival_time":datetime(2026,5,25,17,30),
     "price":750,"ac":False,"total_seats":48,"available_seats":48},
    # Cox's Bazar → Dhaka
    {"id":"R5","operator":"Shohag Paribahan","source":"Cox's Bazar","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,22,0),"arrival_time":datetime(2026,5,26,8,0),
     "price":1200,"ac":True,"total_seats":36,"available_seats":36},
    # Rajshahi → Dhaka
    {"id":"R6","operator":"Hanif Enterprise","source":"Rajshahi","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,6,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":1100,"ac":True,"total_seats":36,"available_seats":36},
    # Khulna → Dhaka
    {"id":"R7","operator":"Shohag Paribahan","source":"Khulna","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":1000,"ac":True,"total_seats":40,"available_seats":40},
    # Comilla → Dhaka
    {"id":"R8","operator":"TR Travels","source":"Comilla","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,11,0),
     "price":400,"ac":False,"total_seats":48,"available_seats":48},
    # Barisal → Dhaka
    {"id":"R9","operator":"Shohag Paribahan","source":"Barisal","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,6,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":900,"ac":True,"total_seats":36,"available_seats":36},
    # Kishoreganj → Dhaka (the missing one)
    {"id":"R10","operator":"Anondo Paribahan","source":"Kishoreganj","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,7,30),"arrival_time":datetime(2026,5,25,10,30),
     "price":350,"ac":False,"total_seats":40,"available_seats":40},
    # Chandpur → Dhaka
    {"id":"R11","operator":"Meghna Express","source":"Chandpur","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,13,0),
     "price":500,"ac":False,"total_seats":44,"available_seats":44},
    # Mymensingh → Dhaka
    {"id":"R12","operator":"Ena Transport","source":"Mymensingh","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":400,"ac":False,"total_seats":44,"available_seats":44},
    # Rangpur → Dhaka
    {"id":"R13","operator":"Hanif Enterprise","source":"Rangpur","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":1000,"ac":True,"total_seats":40,"available_seats":40},
    # Bogra → Dhaka
    {"id":"R14","operator":"Shyamoli Paribahan","source":"Bogra","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,7,0),"arrival_time":datetime(2026,5,25,12,0),
     "price":700,"ac":False,"total_seats":44,"available_seats":44},
    # Jessore → Dhaka
    {"id":"R15","operator":"Shohag Paribahan","source":"Jessore","destination":"Dhaka",
     "departure_time":datetime(2026,5,25,9,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":1100,"ac":True,"total_seats":40,"available_seats":40},
    # Chittagong → Sylhet (reverse of B34)
    {"id":"R16","operator":"Ena Transport","source":"Chittagong","destination":"Sylhet",
     "departure_time":datetime(2026,5,25,7,0),"arrival_time":datetime(2026,5,25,15,0),
     "price":1200,"ac":False,"total_seats":44,"available_seats":44},
    # Cox's Bazar → Chittagong (reverse of B35)
    {"id":"R17","operator":"Green Line","source":"Cox's Bazar","destination":"Chittagong",
     "departure_time":datetime(2026,5,25,8,0),"arrival_time":datetime(2026,5,25,11,30),
     "price":600,"ac":True,"total_seats":36,"available_seats":36},
    # Khulna → Rajshahi (reverse of B36)
    {"id":"R18","operator":"Hanif Enterprise","source":"Khulna","destination":"Rajshahi",
     "departure_time":datetime(2026,5,25,10,0),"arrival_time":datetime(2026,5,25,17,0),
     "price":950,"ac":False,"total_seats":44,"available_seats":44},
    # Chandpur → Kishoreganj (reverse of B37)
    {"id":"R19","operator":"Local Express","source":"Chandpur","destination":"Kishoreganj",
     "departure_time":datetime(2026,5,25,10,0),"arrival_time":datetime(2026,5,25,14,0),
     "price":450,"ac":False,"total_seats":40,"available_seats":40},
]

async def seed():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as session:
        existing = (await session.execute(select(BusRoute))).scalars().first()
        if existing:
            print("Database already seeded. Delete travel_ai.db to re‑seed from scratch.")
            return
        for bus in BUS_SEED_DATA:
            session.add(BusRoute(**bus))
        await session.commit()
        print(f"Database seeded successfully with {len(BUS_SEED_DATA)} routes (including returns).")

if __name__ == "__main__":
    asyncio.run(seed())