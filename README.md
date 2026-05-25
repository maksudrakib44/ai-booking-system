
## 🚌 RouteMind AI — AI-Powered Travel Booking Copilot

**RouteMind AI** is an intelligent, conversational travel assistant for bus booking in Bangladesh.  
It understands natural language, searches real bus schedules, compares options, remembers user preferences, and completes bookings step by step — just like a human travel agent.

Built with **LangGraph**, **Gemini 2.5 Flash**, **FastAPI**, **Redis**, **SQLite**, and a modern **Streamlit** UI.

---

## 🧠 Key AI Features

- **Conversational AI** – talk to the assistant naturally (text / voice‑ready)
- **Tool‑calling Agent** – LLM automatically uses search, availability, and booking tools
- **Flexible Date Understanding** – “today”, “tomorrow”, “next Monday”, “within 7 days”
- **Smart Recommendations** – filters by budget, AC/non‑AC, time, and speed
- **Personalised Experience** – remembers preferences via a lightweight token (`X-User-Token`)
- **Seat Preference Handling** – “not first row”, “window”, “aisle”
- **Multi‑turn Booking Flow** – confirms details and waits for user approval before booking
- **Real Database** – dynamic schedules, independent seat availability per day & bus
- **Caching** – Redis caches route searches for instant responses


---

## 🏗️ Architecture

```
┌─────────────┐       ┌──────────────┐       ┌─────────────────┐
│  Streamlit  │◄─REST─►│  FastAPI     │       │  LangGraph      │
│  Frontend   │       │  Gateway     │       │  AI Orchestrator│
└─────────────┘       └──────┬───────┘       └────────┬────────┘
                             │                        │
                             │                        ▼
                             │             ┌─────────────────────┐
                             │             │   Agent Nodes       │
                             │             │  - agent_node (LLM) │
                             │             │  - tool_node (tools)│
                             │             └──────────┬──────────┘
                             │                        │
                             ▼                        ▼
                    ┌────────────────┐     ┌──────────────────────┐
                    │   Redis        │     │  Tools & Integrations│
                    │ (session/cache)│     │  - SQLite DB         │
                    └────────────────┘     │  - Gemini LLM        │
                                           └──────────────────────┘
```

**Flow**: User message → FastAPI → LangGraph agent → Tools (DB queries) → LLM reasoning → Response → Streamlit UI

---

## 🛠️ Tech Stack

| Layer          | Technology |
|----------------|------------|
| **Frontend**   | Streamlit (Python) |
| **Backend**    | FastAPI, Uvicorn |
| **AI / Agent** | LangGraph, LangChain |
| **LLM**        | Google Gemini 2.5 Flash (free tier) |
| **Database**   | SQLite (async via aiosqlite) |
| **Memory & Cache** | Redis |
| **Timezone**   | pytz (Asia/Dhaka) |
| **Auth**       | Lightweight token (`X-User-Token`) |
| **Deployment** | Docker, Streamlit Cloud (frontend), Render/Railway (backend) |

---

## 🚀 Quick Start (Local)

### Prerequisites
- Python 3.11+
- Redis (running on `localhost:6379`)
- Gemini API key ([get one free](https://aistudio.google.com/apikey))

### 1. Clone the repository
```bash
git clone https://github.com/maksudrakib44/ai-booking-system.git
cd ai-booking-system
```

### 2. Set up environment
```bash
python -m venv venv
source venv/bin/activate   # Linux/Mac
venv\Scripts\activate      # Windows
pip install -r requirements.txt
```

### 3. Configure environment variables
Copy `.env.example` to `.env` and fill in your keys:
```
GEMINI_API_KEY=your-gemini-api-key
REDIS_URL=redis://localhost:6379/0
DATABASE_URL=sqlite+aiosqlite:///./travel_ai.db
```

### 4. Seed the database
```bash
python -m app.database.seed
```

### 5. Start Redis
```bash
redis-server
```

### 6. Run the backend
```bash
uvicorn app.main:app --reload
```
Backend runs on http://localhost:8000.  
Interactive API docs: http://localhost:8000/docs

### 7. Run the Streamlit frontend (optional)
```bash
streamlit run streamlit_app.py
```
Frontend runs on http://localhost:8501

---

## 🔍 Testing with Swagger UI

1. Open http://localhost:8000/docs
2. Use `POST /api/v1/chat` with a request like:
```json
{
  "message": "Find me the cheapest AC bus from Dhaka to Kishoreganj tomorrow."
}
```
3. Continue the conversation using the returned `session_id`.

---

## 📁 Project Structure

```
.
├── app/
│   ├── main.py                  # FastAPI entrypoint
│   ├── config.py                # Settings from .env
│   ├── dependencies.py          # X-User-Token user identification
│   ├── routes/
│   │   └── chat.py              # /chat endpoint
│   ├── ai/
│   │   ├── agents/
│   │   │   ├── graph.py         # LangGraph agent definition
│   │   │   └── state.py         # Agent state type
│   │   ├── tools/
│   │   │   └── bus_tools.py     # search, check, book tools
│   │   ├── prompts/
│   │   │   └── system_prompt.py # LLM system prompt
│   │   └── ...
│   ├── database/
│   │   ├── session.py           # Async SQLAlchemy session
│   │   ├── models.py            # ORM models (User, BusRoute, Booking)
│   │   └── seed.py              # Seed 7‑day bus schedules
│   ├── models/
│   │   └── schemas.py           # Pydantic schemas
│   └── services/
│       └── redis_service.py     # Redis session & cache management
├── streamlit_app.py             # Modern chat UI
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

---

## 🧪 Example Conversations

**User**: "Any non‑AC buses from Dhaka to Kishoreganj tomorrow morning?"  
**Agent**: Searches with `date="tomorrow"`, filters by AC=false, suggests suitable buses.

**User**: "Book 2 window seats, not first row."  
**Agent**: Confirms bus details, asks for final permission, then books seats with `seat_preference="window, not first row"`.

**User**: "What about the day after tomorrow?"  
**Agent**: Calls `search_bus_routes` with `date="day after tomorrow"` and shows fresh results.

---

## 🚢 Deployment

### Backend (FastAPI)
- Use **Render**, **Railway**, **Fly.io**, or a VPS.
- Set the environment variables (`GEMINI_API_KEY`, `DATABASE_URL`, `REDIS_URL`) in the platform.
- For simplicity, you can use SQLite and Redis hosted in the cloud (e.g., Redis Cloud).

### Frontend (Streamlit)
- Push the repository to GitHub.
- Go to [share.streamlit.io](https://share.streamlit.io) and deploy `streamlit_app.py`.
- Add a secret `BACKEND_URL` pointing to your deployed FastAPI backend.

---

## 🔮 Future Roadmap

- [ ] Voice input (Whisper) and spoken responses (ElevenLabs)
- [ ] Real payment integration
- [ ] Multi‑city trip planner
- [ ] Real‑time bus tracking
- [ ] Admin dashboard for operators
- [ ] Switch to PostgreSQL for production

---

## 👨‍💻 Author

**Md. Maksudul Haque**  
[GitHub](https://github.com/maksudrakib44) 

---

