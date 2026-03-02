import requests
import streamlit as st
from streamlit_autorefresh import st_autorefresh

BACKEND = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="OnSure Health LLC • Realtime Voice Intelligence",
    layout="wide"
)

st.markdown("""
<style>
html, body, [class*="css"]  {
    font-size: 20px !important;
    color: #111 !important;
}
.stApp { background: linear-gradient(135deg, #fff5f5, #ffe6e6); }
.big-title { font-size: 60px !important; font-weight: 900 !important; color: #b30000 !important; text-align: center; }
.sub-title { font-size: 26px !important; font-weight: 800; color: #cc0000; text-align: center; }
.madeby { font-size: 20px !important; font-weight: 700; color: #800000; text-align: center; margin-bottom: 30px; }
.card { padding: 30px; border-radius: 20px; background: white; border: 3px solid #ff4d4d; box-shadow: 0 10px 30px rgba(255,0,0,0.15); }
.kpi-title { font-size: 18px; font-weight: 800; color: #990000; }
.kpi-value { font-size: 46px; font-weight: 900; color: #cc0000; }
.section-title { font-size: 30px; font-weight: 900; color: #b30000; }
.demo-box { margin-top: 25px; padding: 30px; border-radius: 20px; background: #fff0f0; border: 4px solid #ff0000;
    font-size: 26px; font-weight: 700; color: #660000; line-height: 1.8; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="big-title">🏥 OnSure Health LLC • Realtime Voice Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">👩‍⚕️ Doctor • 👨‍⚕️ Nurse • 🧾 Revenue Cycle • 🇺🇸 US Healthcare</div>', unsafe_allow_html=True)
st.markdown('<div class="madeby">Made by: Lavanya Srivastava</div>', unsafe_allow_html=True)

with st.sidebar:
    st.header("📞 Live Demo")
    refresh = st.slider("Refresh (seconds)", 1, 5, 2)

    # ✅ Stable auto-refresh (NO infinite loop)
    st_autorefresh(interval=refresh * 1000, key="datarefresh")

    if st.button("🚀 Start Demo Call"):
        try:
            r = requests.post(f"{BACKEND}/make_call", timeout=10).json()
            if r.get("ok"):
                st.success("Call Triggered ✅")
            else:
                st.error(r.get("error"))
        except Exception as e:
            st.error("Backend not reachable")
            st.write(str(e))

try:
    data = requests.get(f"{BACKEND}/metrics", timeout=3).json()
    backend_ok = True
except Exception:
    backend_ok = False
    data = {}

col1, col2, col3, col4 = st.columns(4)

def card(title, value):
    return f"""
    <div class="card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}</div>
    </div>
    """

if backend_ok:
    col1.markdown(card("📡 Status", data.get("status", "Idle")), unsafe_allow_html=True)
    col2.markdown(card("🎧 Frames", data.get("frames", "0")), unsafe_allow_html=True)
    col3.markdown(card("⚡ First Note", data.get("time_to_first_transcript_s", "—")), unsafe_allow_html=True)
    col4.markdown(card("🧠 Latency", data.get("last_latency_s", "—")), unsafe_allow_html=True)
else:
    col1.markdown(card("Status", "Backend Offline"), unsafe_allow_html=True)
    col2.markdown(card("Frames", "—"), unsafe_allow_html=True)
    col3.markdown(card("First Note", "—"), unsafe_allow_html=True)
    col4.markdown(card("Latency", "—"), unsafe_allow_html=True)

st.markdown('<div class="section-title">🧾 Live Clinical Notes</div>', unsafe_allow_html=True)

if backend_ok:
    transcripts = data.get("final_transcripts", [])
    if transcripts:
        for t in transcripts[::-1]:
            st.markdown(f"<div class='card'>{t}</div>", unsafe_allow_html=True)
    else:
        st.markdown("<div class='card'>⏳ Waiting for speech...</div>", unsafe_allow_html=True)
else:
    st.markdown("<div class='card'>Start backend: uvicorn server:app --reload</div>", unsafe_allow_html=True)

st.markdown("""
<div class="demo-box">
🎤 DEMO SCRIPT (Speak During Call)

1️⃣ Hello. This is a demo call for insurance check.  
2️⃣ Patient name is John.  
3️⃣ Insurance is Blue Cross.  
4️⃣ Please check if insurance is active today.  
5️⃣ Is approval needed before the visit?  
7️⃣ What is the deductible amount?  
8️⃣ Appointment is at 10 AM today. Please confirm.  
9️⃣ Thank you. Goodbye.
</div>
""", unsafe_allow_html=True)