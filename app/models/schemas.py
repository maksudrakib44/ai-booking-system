from pydantic import BaseModel
from typing import List, Optional, Dict, Any

# ---------- Chat ----------
class ChatRequest(BaseModel):
    message: str
    session_id: Optional[str] = None
    user_id: Optional[str] = None   # fallback if no token header

class ChatResponse(BaseModel):
    session_id: str
    response: str

# ---------- Optional direct API types (not used by the agent) ----------
class BusSearchRequest(BaseModel):
    source: str
    destination: str
    date: Optional[str] = None

class BusOption(BaseModel):
    id: str
    operator: str
    departure: str
    arrival: str
    price: float
    ac: bool
    seats_available: int
    seat_numbers: List[str]

class SeatMapResponse(BaseModel):
    bus_id: str
    operator: str
    seat_map: Dict[str, str]

class BookingRequest(BaseModel):
    user_id: str
    bus_id: str
    seat_numbers: List[str]

class BookingResponse(BaseModel):
    booking_id: str
    status: str
    bus: str
    seats: List[str]
    departure: str
    message: str