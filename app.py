import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
import plotly.graph_objects as go
import base64
from pathlib import Path
from components import create_track_plot, render_track_panel, render_car_panel
from ai_commentary import AICommentarySystem, create_commentary_interface, play_audio

# Try to import WeatherClient (weather API wrapper). If unavailable, we'll fall back to a small mock.
try:
    from weather import WeatherClient
except Exception:
    WeatherClient = None

# Page setup
st.set_page_config(page_title="Lyra", layout="wide", page_icon="components/favicon.ico")

# Custom CSS for gradient theme and animations
def get_css():
    return """
    <style>
    /* Import Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700;900&display=swap');
    
    /* Main gradient background */
    .main .block-container {
        /* Navy blue + dark purple gradient (original look) */
        background: linear-gradient(135deg, #1a0033 0%, #0d1b2a 25%, #1b263b 50%, #0f3460 75%, #16213e 100%);
        background-size: 400% 400%;
        animation: gradientShift 15s ease infinite;
        min-height: 100vh;
        position: relative;
        /* Allow page to scroll */
        overflow-x: hidden;
        overflow-y: auto;
    }

    /* Enable page scroll */
    html, body { height: 100%; overflow-y: auto !important; }
    [data-testid="stAppViewContainer"] { overflow-y: auto; }
    
    @keyframes gradientShift {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Background elements container */
    
    
    /* Animated background elements */
    .bg-element {
        position: absolute;
        opacity: 0.3;
        animation-duration: 20s;
        animation-iteration-count: infinite;
        animation-timing-function: linear;
    }
    
    .sun {
        width: 180px;
        height: 180px;
        top: 10%;
        right: 15%;
        animation-name: orbit;
        animation-duration: 30s;
    }
    
    .planet {
        width: 140px;
        height: 140px;
        top: 20%;
        left: 10%;
        animation-name: float;
        animation-duration: 25s;
    }
    
    .moon {
        width: 60px;
        height: 60px;
        top: 30%;
        right: 25%;
        animation-name: drift;
        animation-duration: 18s;
    }
    
    .star8 {
        width: 50px;
        height: 50px;
        top: 15%;
        left: 20%;
        animation-name: twinkle;
        animation-duration: 3s;
    }
    
    .spark {
        width: 35px;
        height: 35px;
        top: 40%;
        right: 30%;
        animation-name: sparkle;
        animation-duration: 2s;
    }
    
    .spiral-galaxy {
        width: 160px;
        height: 160px;
        bottom: 20%;
        left: 15%;
        animation-name: rotate;
        animation-duration: 40s;
    }
    
    .orbit-rings {
        width: 200px;
        height: 200px;
        bottom: 30%;
        right: 20%;
        animation-name: orbitRings;
        animation-duration: 35s;
    }
    
    .planet-ring {
        width: 130px;
        height: 130px;
        top: 50%;
        left: 5%;
        animation-name: rotate;
        animation-duration: 22s;
    }
    
    /* Animation keyframes */
    @keyframes orbit {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(50px, -30px) rotate(90deg); }
        50% { transform: translate(100px, 0) rotate(180deg); }
        75% { transform: translate(50px, 30px) rotate(270deg); }
        100% { transform: translate(0, 0) rotate(360deg); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-20px) rotate(120deg); }
        66% { transform: translateY(10px) rotate(240deg); }
    }
    
    @keyframes drift {
        0% { transform: translateX(0px) translateY(0px); }
        25% { transform: translateX(30px) translateY(-15px); }
        50% { transform: translateX(60px) translateY(0px); }
        75% { transform: translateX(30px) translateY(15px); }
        100% { transform: translateX(0px) translateY(0px); }
    }
    
    @keyframes twinkle {
        0%, 100% { opacity: 0.3; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.2); }
    }
    
    @keyframes sparkle {
        0% { opacity: 0; transform: scale(0.5) rotate(0deg); }
        50% { opacity: 1; transform: scale(1.2) rotate(180deg); }
        100% { opacity: 0; transform: scale(0.5) rotate(360deg); }
    }
    
    @keyframes rotate {
        from { transform: rotate(0deg); }
        to { transform: rotate(360deg); }
    }
    
    @keyframes orbitRings {
        0% { transform: rotate(0deg) scale(1); }
        50% { transform: rotate(180deg) scale(1.1); }
        100% { transform: rotate(360deg) scale(1); }
    }
    
    /* Main content styling */
    .main .block-container > div {
        background: rgba(0, 0, 0, 0.2);
        backdrop-filter: blur(10px);
        border-radius: 20px;
        padding: 1rem;
        margin: 0.6rem 0;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
    }

    /* Panel helpers for dashboard layout */
    .panel {
        border: 1px solid rgba(0, 255, 209, 0.15);
        border-radius: 14px;
        padding: 0.6rem 0.75rem;
        background: rgba(2, 20, 23, 0.35);
        margin-bottom: 0.75rem;
        position: relative;
        overflow: auto;
        /* draggable via JS; no resize */
        cursor: move;
        z-index: 10;
    }
    
    /* Video panel specific styling */
    .panel video {
        z-index: 15;
        position: relative;
    }
    .panel-title {
        font-family: 'Orbitron', monospace;
        color: #59e1c6;
        font-size: 0.95rem;
        margin: 0 0 0.5rem 0;
        letter-spacing: 0.06em;
        user-select: none;
    }
    .panel-title::after {
        content: "";
        display: block;
        height: 2px;
        margin-top: 6px;
        background: linear-gradient(90deg, rgba(0,230,184,0.85), rgba(0,230,184,0.15));
    }
    .panel::before, .panel::after {
        content: "";
        position: absolute;
        width: 28px; height: 28px;
        border: 2px solid rgba(0,230,184,0.25);
        border-right: none; border-bottom: none;
        top: 6px; left: 6px;
        border-radius: 8px 0 0 0;
    }
    .panel::after {
        top: auto; left: auto; right: 6px; bottom: 6px;
        border-right: 2px solid rgba(0,230,184,0.25);
        border-bottom: 2px solid rgba(0,230,184,0.25);
        border-left: none; border-top: none;
        border-radius: 0 0 8px 0;
    }
    .panel-placeholder {
        width: 100%;
        min-height: 120px;
        border: 1px dashed rgba(255, 255, 255, 0.25);
        border-radius: 10px;
        background: rgba(255,255,255,0.03);
    }

    
    /* Title styling */
    h1 {
        font-family: 'Orbitron', monospace;
        font-weight: 900;
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4, #45b7d1, #96ceb4);
        background-size: 400% 400%;
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        animation: gradientText 3s ease infinite;
        text-align: center;
        margin-bottom: 1.2rem;
        font-size: 2.2rem;
        text-shadow: 0 0 30px rgba(255, 255, 255, 0.5);
    }
    
    @keyframes gradientText {
        0% { background-position: 0% 50%; }
        50% { background-position: 100% 50%; }
        100% { background-position: 0% 50%; }
    }
    
    /* Subtitle styling */
    .subtitle {
        font-family: 'Orbitron', monospace;
        color: #a8dadc;
        text-align: center;
        font-size: 1rem;
        margin-bottom: 1rem;
        text-shadow: 0 0 10px rgba(168, 218, 220, 0.5);
    }
    
    /* Section headers */
    h2, h3 {
        font-family: 'Orbitron', monospace;
        color: #f1faee;
        text-shadow: 0 0 10px rgba(241, 250, 238, 0.3);
    }
    
    /* Plotly chart styling */
    .js-plotly-plot {
        background: rgba(0, 0, 0, 0.3) !important;
        border-radius: 15px !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
    }
    
    /* Decision card styling */
    .decision-card {
        background: linear-gradient(135deg, rgba(255, 107, 107, 0.2), rgba(78, 205, 196, 0.2));
        border: 2px solid rgba(255, 255, 255, 0.2);
        border-radius: 15px;
        padding: 1rem;
        text-align: center;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
        transition: all 0.3s ease;
        max-width: 300px;
        margin: 0 auto;
    }
    
    .decision-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(0, 0, 0, 0.4);
    }
    
    .decision-card h2 {
        font-size: 1.2rem !important;
        margin-bottom: 0.5rem !important;
    }
    
    .decision-card p {
        font-size: 0.9rem !important;
        margin: 0.3rem 0 !important;
    }
    
    /* Clean inline fuel icon */
    .fuel-inline-container {
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 0.5rem 0;
    }
    
    .fuel-icon-clean {
        width: 28px;
        height: 36px;
        position: relative;
        background: linear-gradient(180deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1.5px solid #a8dadc;
        border-radius: 6px 6px 8px 8px;
        margin-left: 12px;
        overflow: hidden;
        box-shadow: 0 0 8px rgba(168,218,220,0.2);
        transition: all 0.3s ease;
    }
    
    .fuel-icon-clean::before {
        content: '';
        position: absolute;
        top: -3px;
        right: -8px;
        width: 12px;
        height: 8px;
        background: #a8dadc;
        border-radius: 0 3px 3px 0;
        box-shadow: 0 0 4px rgba(168,218,220,0.3);
    }
    
    .fuel-level-clean {
        position: absolute;
        bottom: 0;
        left: 0;
        width: 100%;
        transition: height 0.6s ease-out;
        border-radius: 0 0 6px 6px;
    }
    
    .fuel-level-clean.high {
        background: linear-gradient(180deg, #4ecdc4 0%, #96ceb4 100%);
        box-shadow: 0 0 8px rgba(78,205,196,0.4);
    }
    
    .fuel-level-clean.medium {
        background: linear-gradient(180deg, #f1c40f 0%, #f39c12 100%);
        box-shadow: 0 0 8px rgba(241,196,15,0.4);
    }
    
    .fuel-level-clean.low {
        background: linear-gradient(180deg, #ff6b6b 0%, #e74c3c 100%);
        box-shadow: 0 0 8px rgba(255,107,107,0.5);
        animation: lowFuelPulse 1.5s ease-in-out infinite alternate;
    }
    
    @keyframes lowFuelPulse {
        0% { box-shadow: 0 0 8px rgba(255,107,107,0.5); }
        100% { box-shadow: 0 0 15px rgba(255,107,107,0.8); }
    }
    
    .fuel-ripple {
        position: absolute;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent 40%, rgba(255,255,255,0.1) 50%, transparent 60%);
        animation: fuelRipple 2.5s linear infinite;
        opacity: 0.6;
    }
    
    @keyframes fuelRipple {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
    }
    
    .fuel-label {
        color: #a8dadc;
        font-size: 1rem;
        margin-right: 8px;
        font-family: 'Orbitron', monospace;
    }
    
    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
    }
    
    ::-webkit-scrollbar-track {
        background: rgba(0, 0, 0, 0.2);
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(45deg, #ff6b6b, #4ecdc4);
        border-radius: 4px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(45deg, #ff5252, #26a69a);
    }
    </style>
    """

# Function to encode image to base64
def get_image_base64(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

# Function to encode video to base64
def get_video_base64(video_path):
    with open(video_path, "rb") as video_file:
        return base64.b64encode(video_file.read()).decode()

def render_video(video_path, widget):
    """Render video in the given widget"""
    try:
        video_base64 = get_video_base64(video_path)
        widget.markdown(f'''
        <div class="panel" style="position: relative; z-index: 1000;">
            <div class="panel-title">LIVE CAMERA</div>
            <video width="100%" height="300" autoplay muted loop playsinline style="border-radius: 10px; object-fit: cover; position: relative; z-index: 1001; background: #000;">
                <source src="data:video/mp4;base64,{video_base64}" type="video/mp4">
                Your browser does not support the video tag.
            </video>
        </div>
        ''', unsafe_allow_html=True)
    except Exception as e:
        widget.markdown(f'''
        <div class="panel" style="position: relative; z-index: 1000;">
            <div class="panel-title">LIVE CAMERA</div>
            <div style="height: 300px; display: flex; align-items: center; justify-content: center; background: #000; border-radius: 10px; color: white;">
                Video Error: {str(e)}
            </div>
        </div>
        ''', unsafe_allow_html=True)

# Function to create background elements HTML
def create_background_elements():
    elements_dir = Path("Elements")
    elements_html = '<div class="background-elements">'
    
    # Define element configurations
    elements_config = [
        ("sun.png", "sun"),
        ("planet.png", "planet"),
        ("moon.png", "moon"),
        ("star8.png", "star8"),
        ("spark.png", "spark"),
        ("spiral_galaxy.png", "spiral-galaxy"),
        ("orbit_rings.png", "orbit-rings"),
        ("planet_ring.png", "planet-ring")
    ]
    
    for filename, class_name in elements_config:
        image_path = elements_dir / filename
        if image_path.exists():
            img_base64 = get_image_base64(image_path)
            elements_html += f'<img src="data:image/png;base64,{img_base64}" class="bg-element {class_name}" alt="{class_name}">'
    
    elements_html += '</div>'
    return elements_html

# Apply CSS and background elements
st.markdown(get_css(), unsafe_allow_html=True)
st.markdown(create_background_elements(), unsafe_allow_html=True)

# Main content
#st.image('/Users/anudeepbonagiri/Desktop/hackTX v2.0/northmark-dashboard/lyra.png', caption=None, width=100)
st.markdown(
    """
    <div style="text-align: center;">
        <img src="data:image/png;base64,{}" width="167">
    </div>
    """.format(
        # Convert your local image file to a base64 string
        # so it can be embedded directly into the HTML
        base64.b64encode(open('/Users/anudeepbonagiri/Desktop/hackTX v2.0/northmark-dashboard/lyra.png', 'rb').read()).decode()
    ),
    unsafe_allow_html=True
)

# AI Commentary System
commentary_system = AICommentarySystem()
gemini_key, elevenlabs_key, voice_id = create_commentary_interface()


# Enable client-side drag/swap of panels (no external libs)
st.markdown(
    """
    <style>
    .panel.dragging { opacity: 0.7; outline: 1px dashed #59e1c6; }
    .panel.drop-target { box-shadow: inset 0 0 0 2px rgba(89,225,198,0.45); }
    </style>
    <script>
    (function(){
      const init = () => {
        const panels = Array.from(document.querySelectorAll('.panel'));
        let dragSrc = null;
        const swap = (a,b) => {
          if (!a || !b || a===b) return;
          const aParent = a.parentNode, bParent = b.parentNode;
          const aNext = a.nextSibling, bNext = b.nextSibling;
          aParent.insertBefore(b, aNext);
          bParent.insertBefore(a, bNext);
        };
        panels.forEach(p => {
          p.setAttribute('draggable','true');
          p.addEventListener('dragstart', e => {
            dragSrc = p; p.classList.add('dragging');
            try { e.dataTransfer.setData('text/plain', 'panel'); } catch(_){}
            e.dataTransfer.effectAllowed = 'move';
          });
          p.addEventListener('dragend', () => { p.classList.remove('dragging'); panels.forEach(x=>x.classList.remove('drop-target')); });
          p.addEventListener('dragover', e => { e.preventDefault(); e.dataTransfer.dropEffect='move'; p.classList.add('drop-target'); });
          p.addEventListener('dragleave', () => p.classList.remove('drop-target'));
          p.addEventListener('drop', e => { e.preventDefault(); p.classList.remove('drop-target'); if (dragSrc) swap(dragSrc, p); });
        });
      };
      const ready = () => document.readyState === 'complete' || document.readyState === 'interactive';
      if (ready()) setTimeout(init, 0); else document.addEventListener('DOMContentLoaded', init);
    })();
    </script>
    """,
    unsafe_allow_html=True,
)

# Simulation setup
laps = 20
update_interval = 2  # seconds
radius = 100  # track radius

# Generate synthetic telemetry
np.random.seed(42)
data = []
tire_wear = 0
fuel = 100

for lap in range(1, laps + 1):
    lap_time = np.random.normal(90, 2) + (lap * 0.5)
    tire_wear += np.random.uniform(3, 5)
    fuel -= np.random.uniform(3, 6)
    data.append([lap, lap_time, tire_wear, fuel])

df = pd.DataFrame(data, columns=["lap", "lap_time", "tire_wear", "fuel"])

# ----- Layout: three-column dashboard mirroring target UI -----
left_col, center_col, right_col = st.columns([1.2, 1.6, 1.2])

with left_col:
    # Race Status (Track View)
    track_plot = render_track_panel()

    # Live camera video placeholder (will be updated dynamically)
    video_widget = st.empty()
    
    # Initialize with default video
    render_video("F_Lap_Generation_Request.mp4", video_widget)

with center_col:
    # Car visualization from Elements folder
    render_car_panel()

    # Live Commentary button under the car image
    st.markdown('<div class="panel"><div class="panel-title">AI COMMENTARY</div>', unsafe_allow_html=True)
    
    # Commentary button placeholder (will be updated in simulation loop)
    commentary_button_placeholder = st.empty()
    
    st.markdown('</div>', unsafe_allow_html=True)

with right_col:
    # Strategy decision card sits at the top
    decision_card = st.empty()

    # Place Lap Time Trend directly under the decision card
    st.markdown('<div class="panel"><div class="panel-title">LAP TIME TREND</div>', unsafe_allow_html=True)
    lap_chart = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    # Weather section moved to right side
    # Create an updatable placeholder for the weather panel
    weather_widget = st.empty()

    # Default coordinates (Austin, TX). Change to track coordinates if known.
    _weather_lat, _weather_lon = 30.2672, -97.7431

    # Instantiate WeatherClient if available (graceful fallback to mock data)
    _wc = None
    if WeatherClient:
        try:
            _wc = WeatherClient(selected_date=datetime.date.today().isoformat())
        except Exception:
            _wc = None

    def _get_weather_snapshot():
        """Return weather dict with either real data or a mock snapshot."""
        if _wc:
            try:
                epochs = _wc.generate_target_epochs(1)
                target_epoch = int(epochs[0])
                res = _wc.get_weather_at_time(_weather_lat, _weather_lon, target_epoch)
            except Exception as e:
                res = {"error": "exception", "message": str(e)}
        else:
            # Mock data when WeatherClient / network isn't available
            res = {"current": {"temp": 22.4, "humidity": 56.0, "wind_speed": 3.5, "wind_dir": 135.0, "precip": 0.0, "pressure": 1013.5}}
        return res

    # Initial render of the weather panel (will be updated inside simulation loop)
    _res = _get_weather_snapshot()
    if "error" in _res:
        _body = f"<div class='panel'><div class='panel-title'>WEATHER</div><div class='panel-placeholder' style='min-height:120px;padding:12px;'>Error: {_res.get('message','unknown')}</div></div>"
    else:
        _cur = _res["current"]
        _body = f'''
        <div class='panel'>
          <div class='panel-title'>WEATHER</div>
          <div style="padding:12px; min-height:120px; display:flex; gap:12px; align-items:center;">
            <div style="flex:0 0 110px; text-align:center;">
              <div style="font-family: 'Orbitron', monospace; color:#59e1c6; font-size:48px; font-weight:700;">{_cur.get('temp', 0):.1f}°C</div>
              <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:12px;">Current</div>
            </div>
            <div style="flex:1;">
              <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Humidity: <strong style='color:#f1faee'>{_cur.get('humidity', 0):.0f}%</strong></div>
              <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Wind: <strong style='color:#f1faee'>{_cur.get('wind_speed', 0):.1f} m/s</strong> @ {_cur.get('wind_dir', 0):.0f}°</div>
              <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Precip: <strong style='color:#f1faee'>{_cur.get('precip', 0):.1f} mm</strong></div>
              <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Pressure: <strong style='color:#f1faee'>{_cur.get('pressure', 0):.0f} hPa</strong></div>
            </div>
          </div>
        </div>
        '''
    weather_widget.markdown(_body, unsafe_allow_html=True)


# Function to make pit decision
def get_decision(tire_wear, lap_delta):
    if tire_wear > 65 or lap_delta > 0.6:       
        return "PIT NOW", "red"
    elif tire_wear > 45:
        
        return "Monitor Tires", "yellow"
    else:
        return "Stay Out", "green"

# Simulation loop
prev_lap_time = df.loc[0, "lap_time"]

for i in range(len(df)):
    lap = df.loc[i, "lap"]
    lap_time = df.loc[i, "lap_time"]
    tire_wear = df.loc[i, "tire_wear"]
    fuel = df.loc[i, "fuel"]

    # Compute lap delta
    lap_delta = (lap_time - prev_lap_time) / prev_lap_time
    prev_lap_time = lap_time

    # Track plot using component
    fig = create_track_plot(lap, laps, radius)
    track_plot.plotly_chart(fig, use_container_width=True)
    
    # Race Status removed - track visualization only

    # Lap time trend
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=df["lap"][:i+1], 
        y=df["lap_time"][:i+1], 
        mode="lines+markers", 
        name="Lap Time",
        line=dict(color="#4ecdc4", width=3),
        marker=dict(color="#ff6b6b", size=8)
    ))
    fig2.update_layout(
        yaxis_title="Lap Time (s)", 
        xaxis_title="Lap", 
        height=220,
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Orbitron, monospace", color="#f1faee"),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)')
    )
    lap_chart.plotly_chart(fig2, use_container_width=True)
    # Strategy decision with inline fuel icon
    decision, color = get_decision(tire_wear, lap_delta)
    fuel_level_class = "high" if fuel > 60 else "medium" if fuel > 25 else "low"
    fuel_height = max(3, (fuel / 100) * 32)  # 32px is the usable height inside the icon
    
    decision_card.markdown(
        f"""
        <div class="panel">
            <div class="panel-title">STRATEGY DECISION</div>
            <div style="padding: 1rem; text-align: center;">
                <h2 style="color:{color}; font-family: 'Orbitron', monospace; margin-bottom: 1rem; font-size: 1.5rem;">{decision}</h2>
                <p style="color:#f1faee; font-size: 1.1rem; margin: 0.5rem 0;">Lap: {lap}</p>
                <p style="color:#a8dadc; font-size: 1rem; margin: 0.5rem 0;">Tire Wear: {tire_wear:.1f}%</p>
                <div class="fuel-inline-container" style="justify-content: center;">
                    <span class="fuel-label">Fuel: {fuel:.1f}%</span>
                    <div class="fuel-icon-clean">
                        <div class="fuel-level-clean {fuel_level_class}" style="height: {fuel_height}px;">
                            <div class="fuel-ripple"></div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Store current race data in session state for commentary
    st.session_state.current_lap = lap
    st.session_state.current_lap_time = lap_time
    st.session_state.current_tire_wear = tire_wear
    st.session_state.current_fuel = fuel
    st.session_state.current_decision = decision
    st.session_state.current_weather = _cur.get('temp', 0) if '_cur' in locals() else 22.4
    
    # Update commentary button in the loop (no page refresh)
    with commentary_button_placeholder.container():
        # Initialize session state for commentary if not exists
        if 'commentary_generated' not in st.session_state:
            st.session_state.commentary_generated = False
        if 'commentary_text' not in st.session_state:
            st.session_state.commentary_text = ""
        if 'commentary_audio' not in st.session_state:
            st.session_state.commentary_audio = None
        if 'show_commentary' not in st.session_state:
            st.session_state.show_commentary = False
            
        # Create columns for button and status
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if st.button("🎙️ Generate Live Commentary", help="Click to generate AI commentary for current race state", use_container_width=True, key=f"commentary_btn_{i}"):
                if gemini_key and elevenlabs_key and gemini_key != "your_gemini_api_key_here" and elevenlabs_key != "your_elevenlabs_api_key_here":
                    # Store current race state for async processing
                    st.session_state.current_race_stats = {
                        'lap': lap,
                        'lap_time': lap_time,
                        'tire_wear': tire_wear,
                        'fuel': fuel,
                        'decision': decision,
                        'weather': _cur.get('temp', 0) if '_cur' in locals() else 22.4
                    }
                    
                    # Generate commentary without blocking
                    with st.spinner("Generating commentary..."):
                        commentary_text = commentary_system.generate_commentary(st.session_state.current_race_stats)
                        if commentary_text and not commentary_text.startswith("Error"):
                            st.session_state.commentary_text = commentary_text
                            
                            # Generate audio
                            commentary_audio = commentary_system.text_to_speech(commentary_text)
                            if commentary_audio:
                                st.session_state.commentary_audio = commentary_audio
                            
                            st.session_state.commentary_generated = True
                            st.session_state.show_commentary = True
                            st.rerun()
                        else:
                            st.error("Failed to generate commentary text")
                else:
                    st.warning("Please configure your API keys in the .env file!")
        
        with col2:
            if st.session_state.get('show_commentary', False):
                if st.button("❌", help="Close commentary", key=f"close_commentary_{i}"):
                    st.session_state.show_commentary = False
                    st.session_state.commentary_generated = False
                    st.rerun()
        
        # Display commentary if generated
        if st.session_state.get('show_commentary', False) and st.session_state.get('commentary_text', ""):
            st.markdown("**📝 Live Commentary:**")
            with st.container():
                st.info(st.session_state.commentary_text)
                
                if st.session_state.get('commentary_audio'):
                    st.audio(st.session_state.commentary_audio, format="audio/mpeg")
                    
                # Auto-hide after showing (optional)
                if st.button("🔄 Generate New Commentary", key=f"refresh_commentary_{i}"):
                    st.session_state.show_commentary = False
                    st.session_state.commentary_generated = False

    # Video switching based on tire wear
    if tire_wear > 65 and tire_wear < 66:
        video_widget.empty()
        render_video("Pit.mp4", video_widget)
    #else:
        ##video_widget.empty()
        #render_video("F_Lap_Generation_Request.mp4", video_widget)

        # Update weather snapshot each loop to keep it fresh
    try:
                _res = _get_weather_snapshot()
                if "error" in _res:
                        _body = f"<div class='panel'><div class='panel-title'>WEATHER</div><div class='panel-placeholder' style='min-height:120px;padding:12px;'>Error: {_res.get('message','unknown')}</div></div>"
                else:
                        _cur = _res["current"]
                        _body = f'''
                        <div class='panel'>
                            <div class='panel-title'>WEATHER</div>
                            <div style="padding:12px; min-height:120px; display:flex; gap:12px; align-items:center;">
                                <div style="flex:0 0 110px; text-align:center;">
                                    <div style="font-family: 'Orbitron', monospace; color:#59e1c6; font-size:48px; font-weight:700;">{_cur.get('temp', 0):.1f}°C</div>
                                    <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:12px;">Current</div>
                                </div>
                                <div style="flex:1;">
                                    <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Humidity: <strong style='color:#f1faee'>{_cur.get('humidity', 0):.0f}%</strong></div>
                                    <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Wind: <strong style='color:#f1faee'>{_cur.get('wind_speed', 0):.1f} m/s</strong> @ {_cur.get('wind_dir', 0):.0f}°</div>
                                    <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Precip: <strong style='color:#f1faee'>{_cur.get('precip', 0):.1f} mm</strong></div>
                                    <div style="font-family: 'Orbitron', monospace; color:#a8dadc; font-size:14px;">Pressure: <strong style='color:#f1faee'>{_cur.get('pressure', 0):.0f} hPa</strong></div>
                                </div>
                            </div>
                        </div>
                        '''
                weather_widget.markdown(_body, unsafe_allow_html=True)
    except Exception:
                # Swallow rendering errors to avoid breaking simulation loop
                pass

    time.sleep(update_interval)
