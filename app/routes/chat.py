from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
import uuid

from sqlalchemy.ext.asyncio import AsyncSession
from app.ai.agents.graph import app as agent_app
from langchain_core.messages import HumanMessage
from app.services.redis_service import get_session, save_session
from app.database.session import get_db
from app.database.models import User
from app.models.schemas import ChatRequest, ChatResponse
from app.dependencies import get_user_by_token   # token-based user identification

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
async def chat(
    req: ChatRequest,
    user: Optional[User] = Depends(get_user_by_token),
    db: AsyncSession = Depends(get_db)
):
    # Determine user_id: token-based user or fallback
    if user:
        user_id = str(user.id)
    else:
        user_id = req.user_id or "anonymous"

    session_id = req.session_id or str(uuid.uuid4())

    # Load state from Redis
    state = await get_session(session_id)
    if not state:
        state = {
            "messages": [],
            "user_id": user_id,
            "intent": "",
            "entities": {},
            "route_options": [],
            "selected_route": None,
            "booking_details": None,
            "final_response": ""
        }

    # Inject user preferences if available
    if user and user.preferences:
        state["user_preferences"] = user.preferences

    # Append user message
    state["messages"].append(HumanMessage(content=req.message))

    try:
        # Run the LangGraph agent asynchronously
        result = await agent_app.ainvoke(state)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

    # Persist session
    await save_session(session_id, result)

    # Extract final AI response
    ai_messages = [m for m in result["messages"] if m.type == "ai"]
    if not ai_messages:
        raise HTTPException(status_code=500, detail="Agent did not produce a response.")
    reply = ai_messages[-1].content

    return ChatResponse(session_id=session_id, response=reply)