import cv2
import streamlit as st
from ultralytics import YOLO
import time
from collections import deque
import pandas as pd
import io
import requests

# ----------------------------------------------------
# 1. Page Configuration & Theme Setup
# ----------------------------------------------------
st.set_page_config(page_title="Road Analytics Enterprise Suite", layout="wide")

# Custom CSS overrides to strictly enforce the brown and black theme
st.markdown("""
    <style>
        /* Main background */
        .stApp {
            background-color: #12100E !important;
            color: #E6DFD9 !important;
        }
        
        /* Sidebar styling */
        section[data-testid="stSidebar"] {
            background-color: #251F1C !important;
            border-right: 1px solid #3E332E;
        }

        /* Sidebar Text & Label styling */
        section[data-testid="stSidebar"] h1, 
        section[data-testid="stSidebar"] h2, 
        section[data-testid="stSidebar"] h3, 
        section[data-testid="stSidebar"] span, 
        section[data-testid="stSidebar"] p, 
        section[data-testid="stSidebar"] label {
            color: #E6DFD9 !important;
        }

        /* Headings styling */
        h1, h2, h3, h4, h5, h6 {
            color: #D4B296 !important;
            font-family: 'Georgia', serif;
        }

        /* Standard text descriptions */
        .stMarkdown p {
            color: #C5BDB6 !important;
        }

        /* Telemetry Metric Card Styling */
        div[data-testid="metric-container"] {
            background-color: #1C1815 !important;
            border: 1px solid #3E332E !important;
            border-radius: 10px;
            padding: 12px 15px !important;
            box-shadow: 0 4px 6px rgba(0,0,0,0.4);
        }
        div[data-testid="metric-container"] label {
            color: #8B6E60 !important;
            font-weight: bold !important;
            text-transform: uppercase;
            font-size: 0.8rem;
            letter-spacing: 0.05em;
        }
        div[data-testid="metric-container"] div[data-testid="stMetricValue"] {
            color: #D4B296 !important;
            font-family: monospace;
            font-size: 1.8rem;
        }

        /* Streamlit Button custom aesthetic */
        div.stButton > button:first-child {
            background-color: #3E332E !important;
            color: #E6DFD9 !important;
            border: 1px solid #8B6E60 !important;
            border-radius: 8px;
            transition: all 0.3s ease;
            width: 100%;
        }

        div.stButton > button:first-child:hover {
            background-color: #8B6E60 !important;
            color: #12100E !important;
            border-color: #D4B296 !important;
        }

        /* Tab styling */
        button[data-baseweb="tab"] {
            color: #C5BDB6 !important;
            font-weight: bold !important;
        }
        button[aria-selected="true"] {
            color: #D4B296 !important;
            border-color: #D4B296 !important;
        }

        /* Live log console styling (Vertical layout log) */
        .log-container {
            background-color: #1C1815;
            border: 1px solid #3E332E;
            border-radius: 8px;
            padding: 15px;
            height: 200px;
            overflow-y: auto;
            font-family: monospace;
            font-size: 0.85rem;
            box-shadow: inset 0 0 10px rgba(0, 0, 0, 0.8);
        }
        .log-entry {
            margin-bottom: 6px;
            padding-bottom: 4px;
            border-bottom: 1px solid #2A2320;
        }
    </style>
""", unsafe_allow_html=True)

# ----------------------------------------------------
# 2. Session State Initialization (Enterprise Data storage)
# ----------------------------------------------------
if "incident_logs" not in st.session_state:
    st.session_state.incident_logs = deque(maxlen=20)

if "analytics_history" not in st.session_state:
    # Retain structural historical dataframe for business reporting
    st.session_state.analytics_history = pd.DataFrame(columns=["Timestamp", "Pedestrians", "Vehicles", "Heavy Vehicles", "Alerts Active"])

# Pre-configure your unique webhook testing URL in Session State
if "webhook_url" not in st.session_state:
    st.session_state.webhook_url = "https://webhook.site/54188cfa-a030-48c2-89f2-de1fef6d2f28"

# Enable webhook alerts automatically to streamline testing
if "webhook_alert" not in st.session_state:
    st.session_state.webhook_alert = True

# Helper function to append incidents and time-series reports
def log_event(message, event_type="Log"):
    timestamp = time.strftime("%H:%M:%S")
    st.session_state.incident_logs.appendleft(f"[{timestamp}] {message}")

# Cache the model so it doesn't reload on every stream rerun
@st.cache_resource
def load_model():
    return YOLO("yolov8n.pt")

model = load_model()

# ----------------------------------------------------
# 3. Sidebar Enterprise Configurations
# ----------------------------------------------------
st.sidebar.title("🏢 VisionSaaS Control")
st.sidebar.markdown("*Enterprise Road Analytics & Behavior Intelligence*")

st.sidebar.header("Camera Optimization")
confidence_threshold = st.sidebar.slider("AI Confidence Threshold", 0.1, 1.0, 0.45, 0.05)

# Target detection selectors
st.sidebar.write("### Telemetry Filtering")
detect_objects = st.sidebar.checkbox("Track Infrastructure & Road Assets", value=True)
detect_actions = st.sidebar.checkbox("Analyze Behaviors & Safety Violations", value=True)

# Edge guardrail virtual region of interest configuration
st.sidebar.write("### virtual Guardrail Line")
guardrail_y_pct = st.sidebar.slider("Hazard Trigger Line (Vertical %)", 30, 90, 70, 5)

st.sidebar.write("---")
run_stream = st.sidebar.button("🎥 Deploy Live Intelligence Feed")
stop_stream = st.sidebar.button("🛑 Suspend Edge Feed")

# ----------------------------------------------------
# 4. Main Dashboard Enterprise Navigation
# ----------------------------------------------------
st.title("💼 RoadTelemetry Pro - Dashboard")
st.write("Commercial edge solution tracking infrastructure load metrics, hazard notifications, and incident logging.")

# Setup Enterprise Tabs
tab_live, tab_bi, tab_settings = st.tabs([
    "📸 Live Operations Operations", 
    "📈 Business Intelligence & Exports", 
    "⚙️ Notification Hub Configurations"
])

# ----------------------------------------------------
# Feature 1: The Telemetry Bar (Always Rendered at Top level for convenience)
# ----------------------------------------------------
st.write("### 📊 Active Telemetry Bar")
col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
with col_m1:
    metric_ped = st.metric("Active Pedestrians", "0")
with col_m2:
    metric_car = st.metric("Vehicles (Cars/Bikes)", "0")
with col_m3:
    metric_truck = st.metric("Heavy Vehicles (Trucks)", "0")
with col_m4:
    metric_alert = st.metric("Severe Alerts Active", "0")
with col_m5:
    metric_fps = st.metric("System Performance", "0.0 FPS")

st.write("---")

# ----------------------------------------------------
# Tab 1: Live Operations
# ----------------------------------------------------
with tab_live:
    st.write("### Live Camera Intelligence Feed")
    FRAME_WINDOW = st.image([])

    st.write("### 📜 Real-Time Security Incident Stream")
    log_placeholder = st.empty()

    # Log console rendering helper
    def render_log_console():
        log_html = "<div class='log-container'>"
        if len(st.session_state.incident_logs) == 0:
            log_html += "<div class='log-entry' style='color:#8B6E60;'>Enterprise core connected. Awaiting active feed triggers...</div>"
        else:
            for log in st.session_state.incident_logs:
                color = "#E67328" if "ALERT" in log or "⚠️" in log or "🚨" in log else "#C5BDB6"
                log_html += f"<div class='log-entry' style='color:{color};'>{log}</div>"
        log_html += "</div>"
        log_placeholder.markdown(log_html, unsafe_allow_html=True)

    render_log_console()

# ----------------------------------------------------
# Tab 2: Business Intelligence & Exports (The Monetizable Feature)
# ----------------------------------------------------
with tab_bi:
    st.subheader("📊 Analytics Trend Analysis")
    st.write("Continuous frame density metrics computed to track peak congestion times.")

    if not st.session_state.analytics_history.empty:
        # Plot continuous line chart of pedestrians vs cars for logistics/municipal evaluation
        chart_data = st.session_state.analytics_history.set_index("Timestamp")
        st.line_chart(chart_data[["Pedestrians", "Vehicles", "Heavy Vehicles"]])
        
        st.subheader("📥 Export Telemetry Report")
        st.write("Download certified structured telemetry reports to send to compliance or local authorities.")
        
        # Convert Session-State Dataframe to downloadable CSV bytes
        csv_buffer = io.StringIO()
        st.session_state.analytics_history.to_csv(csv_buffer, index=False)
        csv_bytes = csv_buffer.getvalue().encode('utf-8')
        
        st.download_button(
            label="Download Traffic & Congestion Data (CSV)",
            data=csv_bytes,
            file_name=f"road_analytics_report_{time.strftime('%Y%m%d_%H%M%S')}.csv",
            mime="text/csv"
        )
    else:
        st.info("Historical visual telemetry charts will populate once you launch the camera stream.")

# ----------------------------------------------------
# Tab 3: Notification Hub Configurations (B2B SaaS Integration)
# ----------------------------------------------------
with tab_settings:
    st.subheader("🔔 Enterprise Alerts & Integrations")
    st.write("Route localized camera events automatically to emergency teams or operational staff.")
    
    col_set1, col_set2 = st.columns(2)
    with col_set1:
        st.write("#### Alert Channels")
        sms_alert = st.checkbox("Simulate SMS Dispatch", value=True, key="sms_alert")
        webhook_alert = st.checkbox("Forward JSON Payload to Slack Webhook", value=st.session_state.webhook_alert, key="webhook_alert")
        webhook_url = st.text_input(
            "Webhook URL Endpoints", 
            value=st.session_state.webhook_url,
            placeholder="https://hooks.slack.com/services/...", 
            disabled=not st.session_state.get("webhook_alert", False), 
            key="webhook_url"
        )
        
        st.write("---")
        st.write("#### 🧪 Integration Health Check")
        if st.button("🔌 Trigger Test Webhook Alert"):
            test_payload = {
                "text": "🧪 *ROAD TELEMETRY PRO INTEGRATION TEST* 🧪",
                "attachments": [
                    {
                        "color": "#D4B296",
                        "title": "Manual System Connection Test - SUCCESS",
                        "fields": [
                            {"title": "Trigger Origin", "value": "Dashboard Control Panel", "short": True},
                            {"title": "SaaS Pipeline Status", "value": "Operational & Active", "short": True},
                            {"title": "Assigned Channel Target", "value": "General Security Stream", "short": False}
                        ],
                        "footer": "RoadTelemetry Pro Testing Suite",
                        "ts": int(time.time())
                    }
                ]
            }
            try:
                target_url = st.session_state.get("webhook_url", "")
                if target_url:
                    res = requests.post(target_url, json=test_payload, timeout=3.0)
                    if res.status_code in [200, 201]:
                        st.success("✅ Webhook dispatched! Check your Webhook.site tab.")
                        log_event("SUCCESS: Sent manual connection test webhook notification.")
                    else:
                        st.error(f"⚠️ Server responded with status code: {res.status_code}")
                else:
                    st.error("❌ Webhook endpoint URL cannot be empty.")
            except Exception as e:
                st.error(f"❌ Failed to reach connection endpoint: {str(e)}")
        
    with col_set2:
        st.write("#### Alert Customization & Rules")
        alert_cooldown = st.slider("Alert Logging Suppression Cooldown (seconds)", 1, 10, 4, key="alert_cooldown")
        tailgate_margin = st.slider("Tailgate Safety Threshold (Y-Pixel Height Limit)", 350, 480, 410, key="tailgate_margin")

# ----------------------------------------------------
# 5. Helper for Basic Action/Behavior Detection
# ----------------------------------------------------
def analyze_action(bbox, class_name, custom_limit):
    x1, y1, x2, y2 = bbox
    height = y2 - y1
    width = x2 - x1
    aspect_ratio = width / float(height) if height > 0 else 0

    if class_name == "person":
        if aspect_ratio > 1.2:
            return "Person Fallen / Prone ⚠️"
        else:
            return "Walking/Standing"
            
    elif class_name in ["car", "truck", "motorcycle"]:
        # Safety warning triggered if vehicle crosses custom enterprise margin line
        if y2 > custom_limit: 
            return "Tailgating / High Risk 🚨"
        return "Moving Safely"
        
    return "Static"

# ----------------------------------------------------
# 6. Live Video Stream Processing Loop
# ----------------------------------------------------
if run_stream:
    camera = cv2.VideoCapture(0)
    
    if not camera.isOpened():
        st.error("Webcam hardware link failed or permission was denied by OS.")
    else:
        log_event("Success: Established communication channel to localized camera feed.")
        if "render_log_console" in locals():
            render_log_console()
    
    # Accurate RGB colors corresponding to the dark academy style
    theme_bronze = (212, 178, 150)       # Warm Bronze/Gold
    theme_alert = (230, 115, 40)         # Warm Copper/Orange
    theme_brown = (139, 110, 96)         # Soft Copper Brown
    theme_dark_bg = (18, 16, 14)         # Off-black Charcoal
    theme_cream = (230, 223, 217)        # Cream White

    prev_time = time.time()
    log_cooldowns = {"Tailgating": 0, "Prone": 0}

    # Frame skipping helper to avoid UI lag and save compute
    frame_counter = 0

    while camera.isOpened():
        success, frame = camera.read()
        if not success or stop_stream:
            break
        
        frame_counter += 1
        
        # Real-time Processing Rate Calculation (FPS)
        current_time = time.time()
        fps = 1.0 / (current_time - prev_time) if (current_time - prev_time) > 0 else 0.0
        prev_time = current_time

        # Convert BGR (OpenCV default) to RGB (Streamlit display default)
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        frame_height, frame_width, _ = frame_rgb.shape
        
        # Dynamic calculation of virtual guardrail line
        guardline_y_pixel = int((guardrail_y_pct / 100.0) * frame_height)

        # Run model inference
        results = model(frame_rgb, conf=confidence_threshold, verbose=False)
        
        # Initialize trackers
        ped_count = 0
        car_count = 0
        truck_count = 0
        alert_count = 0

        for result in results:
            boxes = result.boxes
            for box in boxes:
                class_id = int(box.cls[0])
                class_name = model.names[class_id]
                
                road_classes = ['person', 'bicycle', 'car', 'motorcycle', 'bus', 'truck', 'traffic light', 'stop sign']
                if class_name not in road_classes:
                    continue
                
                # Increment metrics
                if class_name == 'person':
                    ped_count += 1
                elif class_name in ['car', 'motorcycle', 'bicycle']:
                    car_count += 1
                elif class_name in ['bus', 'truck']:
                    truck_count += 1
                    
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                
                # ----------------------------------------------------
                # Premium Themed Overlay & HUD
                # ----------------------------------------------------
                
                # 1. Bounding Boxes
                if detect_objects:
                    cv2.rectangle(frame_rgb, (x1, y1), (x2, y2), theme_bronze, 2)
                    label = f"{class_name.upper()} {float(box.conf[0]):.2f}"
                    (w, h), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
                    cv2.rectangle(frame_rgb, (x1, y1 - h - 10), (x1 + w + 10, y1), theme_dark_bg, -1)
                    cv2.rectangle(frame_rgb, (x1, y1 - h - 10), (x1 + w + 10, y1), theme_brown, 1)
                    cv2.putText(frame_rgb, label, (x1 + 5, y1 - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.45, theme_cream, 1, cv2.LINE_AA)
                
                # 2. Action Indicators
                if detect_actions:
                    # Leverage session-state parameters directly
                    target_margin = st.session_state.get("tailgate_margin", guardline_y_pixel)
                    action_label = analyze_action((x1, y1, x2, y2), class_name, target_margin)
                    
                    is_hazard = "⚠️" in action_label or "🚨" in action_label
                    
                    if is_hazard:
                        alert_count += 1
                        log_key = "Tailgating" if "Tailgating" in action_label else "Prone"
                        
                        # Fetch throttle limit dynamically from Tab 3 Session State
                        throttle_cooldown = st.session_state.get("alert_cooldown", 4)
                        
                        if current_time - log_cooldowns[log_key] > throttle_cooldown:
                            log_event(f"ENTERPRISE WARNING: {class_name.upper()} behavior flagged -> {action_label}")
                            
                            # Retrieve active dispatch rules securely
                            sms_dispatch = st.session_state.get("sms_alert", True)
                            webhook_dispatch = st.session_state.get("webhook_alert", False)
                            webhook_target = st.session_state.get("webhook_url", "")

                            # Simulated SMS alert trigger
                            if sms_dispatch:
                                log_event("⚡ SMS Dispatched to Operations Manager.", "System")
                            
                            # REAL LIVE Network Hook Dispatch
                            if webhook_dispatch and webhook_target:
                                payload = {
                                    "text": f"🚨 *ROAD INTEL SECURITY ALERT* 🚨",
                                    "attachments": [
                                        {
                                            "color": "#E67328",
                                            "title": "Rule Infraction Detected",
                                            "fields": [
                                                {"title": "Classification", "value": class_name.upper(), "short": True},
                                                {"title": "Flagged Behavior", "value": action_label, "short": True},
                                                {"title": "Y-Coordinate Height", "value": f"{y2}px (Limit: {target_margin}px)", "short": True},
                                                {"title": "Confidence Score", "value": f"{float(box.conf[0]):.2%}", "short": True}
                                            ],
                                            "footer": "VisionSaaS Edge Systems Monitoring",
                                            "ts": int(time.time())
                                        }
                                    ]
                                }
                                try:
                                    response = requests.post(webhook_target, json=payload, timeout=2.5)
                                    if response.status_code == 200 or response.status_code == 201:
                                        log_event(f"🔌 Real-Time Payload Dispatched to: {webhook_target[:28]}...", "System")
                                    else:
                                        log_event(f"⚠️ Webhook payload returned status {response.status_code}.", "System")
                                except Exception as e:
                                    log_event(f"❌ Webhook connection failed: {str(e)}", "System")
                                
                            log_cooldowns[log_key] = current_time

                    action_color = theme_alert if is_hazard else theme_bronze
                    display_text = f"ACTION: {action_label}"
                    (w_act, h_act), _ = cv2.getTextSize(display_text, cv2.FONT_HERSHEY_SIMPLEX, 0.4, 1)
                    
                    bg_y1 = y1 + 5
                    bg_y2 = y1 + h_act + 15
                    
                    cv2.rectangle(frame_rgb, (x1, bg_y1), (x1 + w_act + 10, bg_y2), theme_dark_bg, -1)
                    cv2.rectangle(frame_rgb, (x1, bg_y1), (x1 + w_act + 10, bg_y2), action_color, 1)
                    cv2.putText(frame_rgb, display_text, (x1 + 5, bg_y1 + h_act + 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, action_color, 1, cv2.LINE_AA)
        
        # Draw Visual Region of Interest / Guardrail trigger boundary on the camera feed
        cv2.line(frame_rgb, (0, guardline_y_pixel), (frame_width, guardline_y_pixel), theme_alert, 1, cv2.LINE_AA)
        cv2.putText(frame_rgb, "VIRTUAL HAZARD ZONE THRESHOLD", (10, guardline_y_pixel - 10), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, theme_alert, 1, cv2.LINE_AA)

        # Update dynamic telemetry metric cards
        metric_ped.metric("Active Pedestrians", str(ped_count))
        metric_car.metric("Vehicles (Cars/Bikes)", str(car_count))
        metric_truck.metric("Heavy Vehicles (Trucks)", str(truck_count))
        metric_alert.metric("Severe Alerts Active", str(alert_count))
        metric_fps.metric("System Performance", f"{fps:.1f} FPS")

        # Periodically commit live results to the timeseries dataframe inside session state
        if frame_counter % 10 == 0:
            now_str = time.strftime("%H:%M:%S")
            new_row = pd.DataFrame([{
                "Timestamp": now_str, 
                "Pedestrians": ped_count, 
                "Vehicles": car_count, 
                "Heavy Vehicles": truck_count,
                "Alerts Active": alert_count
            }])
            # Keep history to last 50 data points for performance safety
            st.session_state.analytics_history = pd.concat([st.session_state.analytics_history, new_row]).tail(50)

        # Refresh screen telemetry logs and camera frame
        if "render_log_console" in locals():
            render_log_console()
            
        FRAME_WINDOW.image(frame_rgb)
        
    camera.release()
    log_event("Camera feed safely suspended.")
    if "render_log_console" in locals():
        render_log_console()
    st.info("Live feed suspended.")