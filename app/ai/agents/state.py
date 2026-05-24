from typing import TypedDict, Annotated, Optional
from langgraph.graph.message import add_messages
import operator

class AgentState(TypedDict):
    messages: Annotated[list, add_messages]   # conversation history
    user_id: str
    intent: str
    entities: dict
    route_options: list
    selected_route: Optional[dict]
    booking_details: Optional[dict]
    final_response: str