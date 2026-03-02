import os
import json
import time
import base64
import asyncio
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import Response, PlainTextResponse, JSONResponse
from twilio.rest import Client
import websockets
from dotenv import load_dotenv

# ✅ Always load .env from same folder as this server.py (works even if uvicorn run from elsewhere)
load_dotenv(dotenv_path=Path(__file__).with_name(".env"))

app = FastAPI(title="OnSure Health LLC • Realtime Voice Intelligence")

# =========================
# ENV (from .env)
# =========================
DEEPGRAM_API_KEY = (os.getenv("DEEPGRAM_API_KEY") or "").strip()

TWILIO_ACCOUNT_SID = (os.getenv("TWILIO_ACCOUNT_SID") or "").strip()
TWILIO_API_KEY = (os.getenv("TWILIO_API_KEY") or "").strip()
TWILIO_API_SECRET = (os.getenv("TWILIO_API_SECRET") or "").strip()
TWILIO_FROM_NUMBER = (os.getenv("TWILIO_FROM_NUMBER") or "").strip()
DEMO_TO_NUMBER = (os.getenv("DEMO_TO_NUMBER") or "").strip()

PUBLIC_BASE_URL = (os.getenv("PUBLIC_BASE_URL") or "").strip().rstrip("/")

# =========================
# DEEPGRAM STREAM CONFIG
# =========================
DEEPGRAM_WSS = (
    "wss://api.deepgram.com/v1/listen"
    "?encoding=mulaw"
    "&sample_rate=8000"
    "&channels=1"
    "&interim_results=true"
    "&punctuate=true"
    "&smart_format=true"
    "&endpointing=120"
)

# =========================
# IN-MEMORY STATE (Dashboard reads this)
# =========================
STATE: Dict[str, Any] = {
    "status": "Idle",                  # Idle | Streaming | Disconnected | Error
    "frames": 0,
    "call_sid": None,
    "stream_sid": None,
    "time_to_first_transcript_s": None,
    "last_latency_s": None,
    "final_transcripts": [],
    "last_updated": None,
}

def _reset_state():
    STATE["status"] = "Streaming"
    STATE["frames"] = 0
    STATE["call_sid"] = None
    STATE["stream_sid"] = None
    STATE["time_to_first_transcript_s"] = None
    STATE["last_latency_s"] = None
    STATE["final_transcripts"] = []
    STATE["last_updated"] = time.time()

def _mark_disconnected():
    STATE["status"] = "Disconnected"
    STATE["last_updated"] = time.time()

def build_media_wss_url(request: Request) -> str:
    """
    Twilio will hit your PUBLIC_BASE_URL (ngrok). Host header should be correct.
    Fallback to PUBLIC_BASE_URL if host missing.
    """
    host = (request.headers.get("host") or "").strip()
    if not host:
        host = PUBLIC_BASE_URL.replace("https://", "").replace("http://", "")
    return f"wss://{host}/media"

# =========================
# HEALTH + METRICS
# =========================
@app.get("/")
def health():
    return {
        "status": "ok",
        "service": "OnSure Health LLC • Realtime Voice Intelligence",
        "made_by": "Lavanya Srivastava",
    }

@app.get("/metrics")
def metrics():
    if STATE["status"] == "Streaming" and STATE["last_updated"]:
        if time.time() - STATE["last_updated"] > 30:
            STATE["status"] = "Disconnected"
    return STATE

# =========================
# TWILIO VOICE WEBHOOK (TwiML)
# =========================
@app.api_route("/voice", methods=["GET", "POST"])
async def voice(request: Request):
    if request.method == "GET":
        return PlainTextResponse("VOICE GET OK")

    _reset_state()

    media_wss = build_media_wss_url(request)
    print("✅ /voice POST received from Twilio")
    print("🔗 Streaming to:", media_wss)

    twiml = f"""<?xml version="1.0" encoding="UTF-8"?>
<Response>
  <Say>Welcome to OnSure Health. Connecting you now.</Say>
  <Pause length="1"/>
  <Connect>
    <Stream url="{media_wss}" />
  </Connect>
</Response>"""

    return Response(content=twiml, media_type="application/xml")

# =========================
# TRIGGER CALL (Dashboard button uses this)
# =========================
@app.post("/make_call")
def make_call():
    missing = []
    for k, v in [
        ("PUBLIC_BASE_URL", PUBLIC_BASE_URL),
        ("TWILIO_ACCOUNT_SID", TWILIO_ACCOUNT_SID),
        ("TWILIO_API_KEY", TWILIO_API_KEY),
        ("TWILIO_API_SECRET", TWILIO_API_SECRET),
        ("TWILIO_FROM_NUMBER", TWILIO_FROM_NUMBER),
        ("DEMO_TO_NUMBER", DEMO_TO_NUMBER),
    ]:
        if not v:
            missing.append(k)

    if missing:
        return JSONResponse(
            status_code=400,
            content={"ok": False, "error": f"Missing env vars: {', '.join(missing)}"},
        )

    voice_url = f"{PUBLIC_BASE_URL}/voice"

    try:
        # ✅ correct init for API Key/Secret + Account SID
        client = Client(TWILIO_API_KEY, TWILIO_API_SECRET, TWILIO_ACCOUNT_SID)

        call = client.calls.create(
            url=voice_url,
            method="POST",
            to=DEMO_TO_NUMBER,
            from_=TWILIO_FROM_NUMBER,
        )
        STATE["call_sid"] = call.sid
        return {"ok": True, "call_sid": call.sid, "voice_url": voice_url}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"ok": False, "error": repr(e), "voice_url": voice_url},
        )

# =========================
# MEDIA WEBSOCKET (Twilio -> Deepgram)
# =========================
@app.websocket("/media")
async def media(ws: WebSocket):
    await ws.accept()
    print("✅ Twilio Media Stream connected")

    if not DEEPGRAM_API_KEY:
        print("❌ Missing DEEPGRAM_API_KEY")
        STATE["status"] = "Error"
        STATE["last_updated"] = time.time()
        await ws.close(code=1011)
        return

    dg_headers = {"Authorization": f"Token {DEEPGRAM_API_KEY}"}

    frames = 0
    start_ts = time.time()
    stop_event = asyncio.Event()

    utterance_start_ts: Optional[float] = None
    last_transcript_ts: Optional[float] = None
    first_transcript_ts: Optional[float] = None
    SILENCE_RESET_S = 1.2

    try:
        async with websockets.connect(DEEPGRAM_WSS, extra_headers=dg_headers) as dg_ws:
            print("✅ Deepgram WS connected")

            async def twilio_to_deepgram():
                nonlocal frames
                while True:
                    msg_text = await ws.receive_text()
                    data = json.loads(msg_text)
                    event = data.get("event")

                    if event == "start":
                        start = data.get("start", {})
                        STATE["call_sid"] = start.get("callSid")
                        STATE["stream_sid"] = start.get("streamSid")
                        STATE["status"] = "Streaming"
                        STATE["last_updated"] = time.time()
                        print(f"▶️ start callSid={STATE['call_sid']} streamSid={STATE['stream_sid']}")

                    elif event == "media":
                        frames += 1
                        STATE["frames"] = frames
                        STATE["last_updated"] = time.time()

                        payload_b64 = data["media"]["payload"]
                        audio_bytes = base64.b64decode(payload_b64)
                        await dg_ws.send(audio_bytes)

                    elif event == "stop":
                        print("⏹️ stop from Twilio")
                        _mark_disconnected()
                        stop_event.set()
                        try:
                            await dg_ws.close()
                        except Exception:
                            pass
                        break

            async def deepgram_listener():
                nonlocal utterance_start_ts, last_transcript_ts, first_transcript_ts

                while not stop_event.is_set():
                    try:
                        dg_msg = await dg_ws.recv()
                    except Exception:
                        break

                    if not dg_msg or isinstance(dg_msg, (bytes, bytearray)):
                        continue

                    dg_data = json.loads(dg_msg)
                    alts = dg_data.get("channel", {}).get("alternatives", [])
                    if not alts:
                        continue

                    transcript = (alts[0].get("transcript") or "").strip()
                    if not transcript:
                        continue

                    now = time.time()
                    STATE["last_updated"] = now

                    if first_transcript_ts is None:
                        first_transcript_ts = now
                        STATE["time_to_first_transcript_s"] = round(first_transcript_ts - start_ts, 2)
                        print(f"⚡ Time-to-first-transcript: {STATE['time_to_first_transcript_s']}s")

                    if last_transcript_ts and (now - last_transcript_ts) > SILENCE_RESET_S:
                        utterance_start_ts = None

                    last_transcript_ts = now
                    if utterance_start_ts is None:
                        utterance_start_ts = now

                    is_final = bool(dg_data.get("is_final")) or bool(dg_data.get("speech_final"))
                    if is_final:
                        lat = now - utterance_start_ts
                        STATE["last_latency_s"] = round(lat, 2)
                        STATE["final_transcripts"].append(transcript)
                        STATE["final_transcripts"] = STATE["final_transcripts"][-100:]
                        print(f"📝 FINAL: {transcript}")
                        utterance_start_ts = None

            await asyncio.gather(twilio_to_deepgram(), deepgram_listener())

    except WebSocketDisconnect:
        print("❌ Twilio disconnected (WS closed)")
        _mark_disconnected()
    except Exception as e:
        print("❌ Error:", repr(e))
        STATE["status"] = "Error"
        STATE["last_updated"] = time.time()
    finally:
        stop_event.set()
        try:
            await ws.close()
        except Exception:
            pass
        print("✅ session ended")