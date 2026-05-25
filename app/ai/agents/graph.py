from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from app.ai.agents.state import AgentState
from app.ai.tools.bus_tools import search_bus_routes, check_seat_availability, book_ticket
from app.ai.prompts.system_prompt import SYSTEM_PROMPT
from app.config import settings
from datetime import datetime
import pytz

# Gemini LLM (free tier)
llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.2,
)

tools = [search_bus_routes, check_seat_availability, book_ticket]
llm_with_tools = llm.bind_tools(tools)

async def agent_node(state: AgentState) -> dict:
    """Async agent node – injects user ID, Bangladesh current time, and calls the LLM."""
    messages = state["messages"]
    system_msg = SystemMessage(content=SYSTEM_PROMPT)

    # Let the LLM know which user is talking (so it never asks for user ID)
    user_context = SystemMessage(
        content=f"The current user's ID is '{state['user_id']}'. "
                f"Always use this user_id when calling the book_ticket tool. "
                f"Never ask the user for their user ID."
    )

    # Let the LLM know the exact current date and time in Bangladesh
    now_dhaka = datetime.now(pytz.timezone("Asia/Dhaka"))
    time_context = SystemMessage(
        content=f"The current date and time in Bangladesh is {now_dhaka.strftime('%Y-%m-%d %H:%M:%S')} (Asia/Dhaka). "
                f"When a user asks for 'today' or 'now', use date='today' and the tool will automatically "
                f"show only future departures in Bangladesh local time."
    )

    # Combine all contexts, then add the conversation history
    response = await llm_with_tools.ainvoke(
        [system_msg, user_context, time_context] + messages
    )
    return {"messages": [response]}

def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
    """Route to tools if the last AI message contains tool_calls, else end."""
    last_message = state["messages"][-1]
    if hasattr(last_message, "tool_calls") and last_message.tool_calls:
        return "tools"
    return "__end__"

# Build graph
workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
tool_node = ToolNode(tools)
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")

app = workflow.compile()