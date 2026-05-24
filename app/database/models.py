# This file defines the SQLAlchemy models for the application, representing the database schema for users, bus routes, and bookings. Each model corresponds to a table in the database and includes fields with appropriate data types and relationships.

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.orm import declarative_base
from datetime import datetime

Base = declarative_base()

# User model to represent users of the system, with token-based authentication and preferences.
class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    preferences = Column(JSON, default={})
    created_at = Column(DateTime, default=datetime.utcnow)

# BusRoute model to represent available bus routes with details about stops, times, and pricing.
class BusRoute(Base):
    __tablename__ = "bus_routes"
    id = Column(String, primary_key=True)
    operator = Column(String)
    source = Column(String)
    destination = Column(String)
    departure_time = Column(DateTime)
    arrival_time = Column(DateTime)
    price = Column(Float)
    ac = Column(Boolean, default=False)
    total_seats = Column(Integer)
    available_seats = Column(Integer)

# Booking model to represent ticket bookings made by users, linking to bus routes and storing seat information.
class Booking(Base):
    __tablename__ = "bookings"
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)   # nullable for anonymous
    bus_id = Column(String, ForeignKey("bus_routes.id"))
    seat_numbers = Column(JSON)
    total_price = Column(Float)
    status = Column(String, default="confirmed")
    created_at = Column(DateTime, default=datetime.utcnow)
    