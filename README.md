# RealtimeVoiceOrchestrator

End-to-end real-time Voice AI gateway:
Twilio Media Streams ↔ OpenAI Realtime ↔ Monitoring UI

## Run
uvicorn app.main:app --reload
streamlit run ui/dashboard.py
ngrok http 8000
