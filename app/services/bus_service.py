# Optional service layer (currently direct tool calls are sufficient).
# You can add business logic here later.
from app.database.mock_bus_data import BUS_DATA

def get_all_routes():
    return BUS_DATA