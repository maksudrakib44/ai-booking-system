from typing import Literal
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq
from app.ai.agents.state import AgentState
from app.ai.tools.bus_tools import search_bus_routes, check_seat_availability, book_ticket
from app.ai.prompts.system_prompt import SYSTEM_PROMPT
from app.config import settings

# Free Groq model with very high rate limits (14,400 requests/day)
llm = ChatGroq(
    model="llama-3.1-8b-instant",
    api_key=settings.GROQ_API_KEY,
    temperature=0.2,
)

tools = [search_bus_routes, check_seat_availability, book_ticket] # Define available tools for the agent 
llm_with_tools = llm.bind_tools(tools) # this allows the LLM to call these tools during the conversation

async def agent_node(state: AgentState) -> dict:
    """Async agent node – awaits the LLM call and returns updated state.""" # The state is a dict that includes the conversation history and any other relevant info. The LLM can read and update this state.
    messages = state["messages"]
    system_msg = SystemMessage(content=SYSTEM_PROMPT)
    # Use async invocation to avoid blocking the event loop
    response = await llm_with_tools.ainvoke([system_msg] + messages)
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
tool_node = ToolNode(tools)          # ToolNode awaits async tools automatically
workflow.add_node("tools", tool_node)

workflow.set_entry_point("agent")
workflow.add_conditional_edges("agent", should_continue)
workflow.add_edge("tools", "agent")  # loop back after tool execution

app = workflow.compile()