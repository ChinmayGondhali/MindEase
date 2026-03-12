# 🧠 MindEase — AI-Driven Mental Wellness Platform

**PS06 Hackathon Project** | Python FastAPI + Firebase + Sentiment Wave

---

## 📁 Project Structure

```
mindease/
├── backend/
│   ├── main.py              ← FastAPI app entry point
│   ├── database.py          ← Firebase connection + Mock fallback
│   ├── models.py            ← Pydantic schemas
│   ├── auth_utils.py        ← JWT authentication
│   ├── sentiment.py         ← Sentiment analysis engine
│   ├── requirements.txt     ← Python dependencies
│   ├── .env.example         ← Environment variables template
│   └── routers/
│       ├── auth.py          ← /api/auth  (register, login, me)
│       ├── chat.py          ← /api/chat  (send, history, clear)
│       └── crisis.py        ← /api/crisis (logs, helplines)
└── frontend/
    └── templates/
        └── index.html       ← Full frontend (single file)
```

---

## 🚀 Setup & Run

### Step 1 — Install dependencies
```bash
cd backend
pip install -r requirements.txt
```

### Step 2 — Firebase Setup (Optional — app works without it in Demo mode)

1. Go to [Firebase Console](https://console.firebase.google.com)
2. Create project → Project Settings → Service Accounts
3. Click **"Generate new private key"** → download JSON
4. Rename it to `firebase_credentials.json` and place in `backend/`

### Step 3 — Environment variables
```bash
cd backend
cp .env.example .env
# Edit .env with your values
```

### Step 4 — Run the server
```bash
cd backend
python main.py
```

Open → **http://localhost:8000**

---

## 🔥 Features

### 🌊 Sentiment Wave (Unique Feature)
- Every message is scored from **-100 (crisis) to +100 (positive)**
- Live animated bezier curve graph updates after each message
- Color transitions: Green → Yellow → Orange → Red
- **Danger Zone** visual marker on graph
- Crisis detected → **Auto helpline banner** pops up

### 🔐 Authentication
- JWT-based secure login/signup
- Passwords hashed with bcrypt
- Guest mode (no login needed)
- Token stored in localStorage

### 💬 Chat with Crisis Detection
- Messages saved to Firebase per user
- Sentiment scored on every message
- Crisis logs auto-saved to `crisis_logs` collection
- Bot reply adapts based on sentiment level

### 🗄️ Firebase Collections
| Collection | Purpose |
|---|---|
| `users` | User profiles + hashed passwords |
| `chats/{uid}/messages` | Per-user chat history |
| `crisis_logs` | Auto-logged crisis events |

---

## 📡 API Endpoints

### Auth
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Create account |
| POST | `/api/auth/login` | Login |
| GET  | `/api/auth/me` | Get current user |

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/chat/send` | Send message + get AI reply |
| GET  | `/api/chat/history` | Load chat history |
| DELETE | `/api/chat/history` | Clear chat history |

### Crisis
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET  | `/api/crisis/logs` | Get user's crisis logs |
| PATCH | `/api/crisis/logs/{id}/resolve` | Mark resolved |
| GET  | `/api/crisis/helplines` | Get Indian helplines |

### API Docs (auto-generated)
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## 🧪 Demo Mode (No Firebase needed)
If no Firebase credentials are found, the app runs with an **in-memory mock database**.
All features work — data resets on server restart.

---

## 🏆 Hackathon Highlights
- ✅ **Zero dependencies to run** (demo mode works instantly)
- ✅ **Single-file frontend** served by FastAPI
- ✅ **Unique feature**: Sentiment Wave — no other mental health app has this
- ✅ **Real crisis detection** with auto helpline suggestion
- ✅ **Indian context** — helplines, culturally relevant language
- ✅ **Guest mode** — no friction to start using

---

## Indian Helplines Integrated
| Name | Number | Hours |
|------|--------|-------|
| iCall | 9152987821 | Mon–Sat 8AM–10PM |
| Vandrevala Foundation | 1860-2662-345 | 24/7 |
| NIMHANS | 080-46110007 | 24/7 |
| Snehi | 044-24640050 | 8AM–10PM |
