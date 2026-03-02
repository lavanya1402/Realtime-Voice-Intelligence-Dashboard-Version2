# 🏥 Realtime Voice Intelligence Dashboard – Version 2

A production-ready real-time voice intelligence system built using **Twilio Voice Streaming, Deepgram Realtime Speech-to-Text, FastAPI, and Streamlit**.

This system captures live phone calls, streams audio in real-time, transcribes speech instantly, and visualizes clinical notes along with latency metrics inside a dynamic dashboard.

---

## 🚀 Key Features

* 📞 One-click outbound call trigger
* 🎧 Real-time Twilio media streaming
* 🧠 Deepgram live speech-to-text processing
* ⚡ Time-to-first-transcript measurement
* 📊 Latency tracking per utterance
* 🧾 Live clinical note visualization
* 🔁 Auto-refreshing dashboard
* 🔒 Secure environment variable handling

---

## 🧱 Architecture Overview

```
User → Streamlit Dashboard → FastAPI Backend → Twilio Call
Twilio → Media Stream (WebSocket) → Deepgram
Deepgram → Transcript → FastAPI → Dashboard
```

This project demonstrates real-time streaming architecture with WebSockets and third-party API orchestration.

---

## 🛠 Tech Stack

* **Backend:** FastAPI
* **Telephony:** Twilio Voice API
* **Speech Recognition:** Deepgram Realtime API
* **Frontend Dashboard:** Streamlit
* **Streaming:** WebSockets
* **Language:** Python

---

## 📂 Project Structure

```
.
├── server.py
├── dashboard.py
├── make_call.py
├── check_env.py
├── requirements.txt
├── .env.example
├── ui/
├── scripts/
└── assets/
```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone Repository

```bash
git clone https://github.com/lavanya1402/Realtime-Voice-Intelligence-Dashboard-Version2.git
cd Realtime-Voice-Intelligence-Dashboard-Version2
```

### 2️⃣ Create Virtual Environment

```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Configure Environment Variables

Create a `.env` file:

```
TWILIO_ACCOUNT_SID=
TWILIO_API_KEY=
TWILIO_API_SECRET=
TWILIO_FROM_NUMBER=
DEMO_TO_NUMBER=
DEEPGRAM_API_KEY=
PUBLIC_BASE_URL=
```

⚠️ Never commit real credentials.

---

### 5️⃣ Run Backend

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

### 6️⃣ Run Dashboard

```bash
streamlit run dashboard.py
```

---

## 📊 Dashboard Metrics

* **Status** → Streaming / Disconnected
* **Frames** → Total audio frames received
* **First Note** → Time to first transcript (seconds)
* **Latency** → Real-time transcription latency

---

## 🎤 Demo Flow

1. Click **Start Demo Call**
2. Answer phone
3. Speak demo script
4. Watch live transcript update
5. Observe latency metrics

---

## 🧠 What This Demonstrates

* Real-time event-driven architecture
* WebSocket streaming pipelines
* Telephony AI integration
* Latency optimization tracking
* Production-grade dashboard monitoring

---

## 🔐 Security Notes

* `.env` excluded via `.gitignore`
* API keys not stored in repository
* Public base URL configurable via environment

---

## 👩‍💻 Built By

**Lavanya Srivastava**
AI Developer | Real-Time Systems | Voice Intelligence Architect

---



