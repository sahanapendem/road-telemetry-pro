import streamlit as st
from ultralytics import YOLO
import requests
import av
import pandas as pd
import time
from streamlit_webrtc import webrtc_streamer, VideoTransformerBase

# --- Page Setup & Theme ---
st.set_page_config(page_title="RoadTelemetry Pro", layout="wide")

st.markdown("""
    <style>
        .stApp { background-color: #12100E; color: #E6DFD9; }
        section[data-testid="stSidebar"] { background-color: #251F1C; }
        h1, h2, h3 { color: #D4B296 !important; }
        div[data-testid="metric-container"] { background-color: #1C1815; border: 1px solid #3E332E; }
    </style>
""", unsafe_allow_html=True)

# --- Logic & Model ---
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# Browser-Compatible Processor
class RoadTransformer(VideoTransformerBase):
    def recv(self, frame: av.VideoFrame) -> av.VideoFrame:
        img = frame.to_ndarray(format="rgb24")
        # Confidence threshold from sidebar could be passed here
        results = model(img, conf=st.session_state.get("conf", 0.45), verbose=False)
        annotated_frame = results[0].plot()
        return av.VideoFrame.from_ndarray(annotated_frame, format="rgb24")

# --- Sidebar Control Panel ---
with st.sidebar:
    st.title("🏢 VisionSaaS Control")
    st.markdown("*Enterprise Road Analytics & Behavior Intelligence*")
    
    st.subheader("Camera Optimization")
    st.session_state.conf = st.slider("AI Confidence Threshold", 0.0, 1.0, 0.45)
    
    st.subheader("Telemetry Filtering")
    st.checkbox("Track Infrastructure & Road Assets", value=True)
    st.checkbox("Analyze Behaviors & Safety Violations", value=True)
    
    st.subheader("Virtual Guardrail Line")
    st.slider("Hazard Trigger Line (Vertical %)", 0, 100, 70)
    
    st.button("🎥 Deploy Live Intelligence Feed")

# --- UI ---
st.title("💼 RoadTelemetry Pro - Enterprise Suite")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Active Pedestrians", "0")
col2.metric("Vehicles", "0")
col3.metric("Heavy Trucks", "0")
col4.metric("Severe Alerts", "0")

tab_live, tab_settings = st.tabs(["📸 Live Operations", "⚙️ Notification Hub"])

with tab_live:
    st.write("### Live Camera Intelligence Feed")
    webrtc_streamer(
        key="road-feed",
        video_transformer_factory=RoadTransformer,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={"video": True, "audio": False}
    )

with tab_settings:
    st.write("### Notification Hub Configurations")
    webhook_url = st.text_input("Webhook URL", value="https://webhook.site/54188cfa-a030-48c2-89f2-de1fef6d2f28")
    if st.button("🔌 Trigger Test Webhook"):
        try:
            requests.post(webhook_url, json={"status": "test_alert"}, timeout=3)
            st.success("Test Alert Dispatched Successfully!")
        except Exception as e:
            st.error(f"Error: {e}")