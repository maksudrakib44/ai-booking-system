import streamlit as st
import requests
import uuid
from datetime import datetime

# ---------- Page Config ----------
st.set_page_config(
    page_title="RouteMind AI",
    page_icon="🚌",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- Custom CSS ----------
st.markdown("""
<style>
    /* Modern theme */
    .main-header {
        font-size: 2.5rem;
        font-weight: 700;
        color: #1E3A8A;
        text-align: center;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #64748B;
        text-align: center;
        margin-bottom: 2rem;
    }
    .chat-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .chat-bubble {
        padding: 12px 18px;
        border-radius: 18px;
        margin-bottom: 12px;
        max-width: 85%;
        word-wrap: break-word;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        animation: fadeIn 0.3s ease-in;
    }
    .user-bubble {
        background: linear-gradient(135deg, #3B82F6, #1D4ED8);
        color: white;
        margin-left: auto;
        border-bottom-right-radius: 4px;
    }
    .assistant-bubble {
        background: #F1F5F9;
        color: #1E293B;
        margin-right: auto;
        border-bottom-left-radius: 4px;
        border: 1px solid #E2E8F0;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: #0F172A;
        color: #94A3B8;
        text-align: center;
        padding: 8px;
        font-size: 0.9rem;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .stTextInput input {
        border-radius: 20px;
        border: 2px solid #E2E8F0;
        padding: 12px 20px;
        font-size: 1rem;
    }
    .stButton button {
        border-radius: 20px;
        background: #3B82F6;
        color: white;
        border: none;
        padding: 8px 24px;
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
if "dark_mode" not in st.session_state:
    st.session_state.dark_mode = False

# ---------- Header ----------
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown('<div class="main-header">🚌 RouteMind AI</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Your intelligent travel copilot — Your Journey, One Conversation Away. </div>', unsafe_allow_html=True)

# ---------- Sidebar ----------
with st.sidebar:
    st.title("⚙️ Settings")
    
    # API URL
    api_url = st.text_input("Backend URL", value="http://localhost:8000/api/v1/chat")
    
    # User Token
    user_token = st.text_input("Your Identity Token", 
                               value=st.session_state.user_token,
                               help="A unique string to remember your preferences. Leave empty for anonymous.")
    if user_token != st.session_state.user_token:
        st.session_state.user_token = user_token
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.success("Token updated! Starting fresh session.")
    
    st.divider()
    
    # Session Info
    st.caption(f"Session: {st.session_state.session_id[:8]}...")
    if st.session_state.user_token:
        st.caption(f"User: {st.session_state.user_token}")
    
    st.divider()
    
    # Actions
    if st.button("🧹 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.rerun()
    
    st.divider()
    st.markdown("**RouteMind AI** v1.0")
    st.markdown("Powered by Gemini & LangGraph")

# ---------- Main Chat Area ----------
st.markdown('<div class="chat-container">', unsafe_allow_html=True)

# Display messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(
            f'<div class="chat-bubble user-bubble">🧑‍💻 {msg["content"]}</div>', 
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div class="chat-bubble assistant-bubble">🚌 {msg["content"]}</div>', 
            unsafe_allow_html=True
        )

st.markdown('</div>', unsafe_allow_html=True)

# ---------- Chat Input ----------
prompt = st.chat_input("Where would you like to go today?")

if prompt:
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    
    # API call
    headers = {"Content-Type": "application/json"}
    if st.session_state.user_token:
        headers["X-User-Token"] = st.session_state.user_token
    
    payload = {
        "message": prompt,
        "session_id": st.session_state.session_id,
        "user_id": st.session_state.user_token if st.session_state.user_token else "anonymous"
    }
    
    with st.spinner("🤔 Searching..."):
        try:
            resp = requests.post(api_url, json=payload, headers=headers, timeout=30)
            if resp.status_code == 200:
                data = resp.json()
                reply = data["response"]
                st.session_state.session_id = data["session_id"]
                st.session_state.messages.append({"role": "assistant", "content": reply})
                st.rerun()  # refresh to show new messages
            else:
                error_msg = f"❌ Backend error: {resp.status_code}"
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
                st.rerun()
        except Exception as e:
            st.error(f"🚫 Connection failed: {e}")

# ---------- Footer ----------
st.markdown("---")
col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.markdown(
        "<div style='text-align: center; color: #64748B; padding: 16px;'>"
        "Built with ❤️ by <strong>Md. Maksudul Haque</strong><br>"
        "© 2026 RouteMind AI — AI-Powered Travel Booking Assistant"
        "</div>",
        unsafe_allow_html=True
    )