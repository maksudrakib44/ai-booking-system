import streamlit as st
import asyncio
import uuid
from datetime import datetime
import pytz

# LangChain / LangGraph
from langchain_core.messages import HumanMessage
from app.ai.agents.graph import app as agent_app
from app.dependencies import get_user_by_token
from app.database.models import User
from app.database.seed import seed

# ---------- Page Config ----------
st.set_page_config(page_title="RouteMind AI", page_icon="🚌", layout="centered")

# ---------- Custom CSS ----------
st.markdown("""
<style>
.chat-bubble {
    padding: 12px 16px;
    border-radius: 16px;
    margin-bottom: 8px;
    max-width: 80%;
    word-wrap: break-word;
}
.user-bubble {
    background-color: #e0f0ff;
    margin-left: auto;
    text-align: right;
}
.assistant-bubble {
    background-color: #f0f0f0;
    margin-right: auto;
}
</style>
""", unsafe_allow_html=True)

# ---------- Session State ----------
if "messages" not in st.session_state:
    st.session_state.messages = []
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "user_token" not in st.session_state:
    st.session_state.user_token = ""
if "agent_state" not in st.session_state:
    st.session_state.agent_state = {
        "messages": [],
        "user_id": "anonymous",
        "intent": "",
        "entities": {},
        "route_options": [],
        "selected_route": None,
        "booking_details": None,
        "final_response": ""
    }

# ---------- Header ----------
st.title("🚌 RouteMind AI")
st.caption("Your intelligent travel booking copilot — ask me anything about buses!")

# ---------- Sidebar ----------
with st.sidebar:
    st.subheader("⚙️ Settings")
    user_token = st.text_input("Your User Token", value=st.session_state.user_token,
                               help="Unique string to remember preferences. Empty = anonymous.")
    if user_token != st.session_state.user_token:
        st.session_state.user_token = user_token
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.session_state.agent_state = {
            "messages": [],
            "user_id": "anonymous",
            "intent": "",
            "entities": {},
            "route_options": [],
            "selected_route": None,
            "booking_details": None,
            "final_response": ""
        }
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.agent_state = {
            "messages": [],
            "user_id": "anonymous",
            "intent": "",
            "entities": {},
            "route_options": [],
            "selected_route": None,
            "booking_details": None,
            "final_response": ""
        }
        st.rerun()

# ---------- DB initialisation ----------
@st.cache_resource
def init_db():
    asyncio.run(seed())
    return True

_ = init_db()

# ---------- Display chat ----------
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f'<div class="chat-bubble user-bubble">{msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-bubble assistant-bubble">{msg["content"]}</div>', unsafe_allow_html=True)

# ---------- Input ----------
prompt = st.chat_input("Where would you like to go today?")

if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Resolve user
    user = asyncio.run(get_user_by_token(st.session_state.user_token or None))
    user_id = str(user.id) if user else "anonymous"

    # Update agent state
    state = st.session_state.agent_state
    state["user_id"] = user_id
    if user and user.preferences:
        state["user_preferences"] = user.preferences
    state["messages"].append(HumanMessage(content=prompt))

    # Run agent
    try:
        new_state = asyncio.run(agent_app.ainvoke(state))
    except Exception as e:
        reply = f"❌ Agent error: {e}"
        st.session_state.messages.append({"role": "assistant", "content": reply})
        st.rerun()

    st.session_state.agent_state = new_state

    # Extract reply
    ai_messages = [m for m in new_state["messages"] if m.type == "ai"]
    if ai_messages:
        reply = ai_messages[-1].content
        if isinstance(reply, list):
            reply = "".join(part.get("text", "") for part in reply if part.get("type") == "text")
        st.session_state.messages.append({"role": "assistant", "content": reply})
    else:
        st.session_state.messages.append({"role": "assistant", "content": "I didn't get that."})

    st.rerun()

# ---------- Footer ----------
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #64748B; padding: 16px;'>"
    "Built with ❤️ by <strong>Md. Maksudul Haque</strong><br>"
    "© 2026 RouteMind AI — AI-Powered Travel Booking Assistant"
    "</div>",
    unsafe_allow_html=True
)