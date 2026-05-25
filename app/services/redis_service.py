import json
import redis.asyncio as aioredis
from app.config import settings
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage

redis_client = aioredis.from_url(settings.REDIS_URL, decode_responses=True)

# ----------------------------------------------------------------------
# Session serialisation / deserialisation (unchanged)
# ----------------------------------------------------------------------
def _serialize_state(state: dict) -> dict:
    """Convert LangChain message objects to JSON‑safe dicts."""
    serializable = state.copy()
    if "messages" in serializable:
        serializable["messages"] = [
            {
                "type": m.type,
                "content": m.content,
                **({"tool_calls": m.tool_calls} if hasattr(m, "tool_calls") and m.tool_calls else {}),
                "tool_call_id": getattr(m, "tool_call_id", None),
                "name": getattr(m, "name", None),
            }
            for m in serializable["messages"]
        ]
    return serializable

def _deserialize_state(serialized: dict) -> dict:
    """Convert plain dicts back to LangChain message objects."""
    state = serialized.copy()
    if "messages" in state:
        msg_list = []
        for m in state["messages"]:
            msg_type = m["type"]
            if msg_type == "human":
                msg_list.append(HumanMessage(content=m["content"]))
            elif msg_type == "ai":
                kwargs = {"content": m["content"]}
                if m.get("tool_calls"):
                    kwargs["tool_calls"] = m["tool_calls"]
                msg_list.append(AIMessage(**kwargs))
            elif msg_type == "system":
                msg_list.append(SystemMessage(content=m["content"]))
            elif msg_type == "tool":
                msg_list.append(ToolMessage(
                    content=m["content"],
                    tool_call_id=m.get("tool_call_id"),
                    name=m.get("name")
                ))
        state["messages"] = msg_list
    return state

async def get_session(session_id: str) -> dict | None:
    data = await redis_client.get(f"session:{session_id}")
    if data:
        return _deserialize_state(json.loads(data))
    return None

async def save_session(session_id: str, state: dict):
    serializable = _serialize_state(state)
    await redis_client.set(f"session:{session_id}", json.dumps(serializable), ex=3600)

async def delete_session(session_id: str):
    await redis_client.delete(f"session:{session_id}")

# ----------------------------------------------------------------------
# Route search cache (updated to accept arbitrary cache keys)
# ----------------------------------------------------------------------
async def cache_routes(key: str, routes: str, ttl: int = 300):
    """Cache a route search result under a specific key."""
    await redis_client.set(key, routes, ex=ttl)

async def get_cached_routes(key: str) -> str | None:
    """Retrieve a cached route search by key."""
    return await redis_client.get(key)