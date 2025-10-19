import streamlit as st
import pandas as pd
import numpy as np
import time
import datetime
import plotly.graph_objects as go
import base64
from pathlib import Path
from components import create_track_plot, render_track_panel, render_car_panel

# Try to import WeatherClient (weather API wrapper). If unavailable, we'll fall back to a small mock.
try:
    from weather import WeatherClient
except Exception:
    WeatherClient = None

# Page setup
st.set_page_config(page_title="Race Strategy Dashboard", layout="wide")

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
        width: 200px;
        height: 200px;
        top: 2%;
        right: 2%;
        animation-name: orbit;
        animation-duration: 30s;
    }
    
    .planet {
        width: 160px;
        height: 160px;
        top: 12%;
        left: 1%;
        animation-name: float;
        animation-duration: 25s;
    }
    
    .moon {
        width: 70px;
        height: 70px;
        top: 20%;
        right: 12%;
        animation-name: drift;
        animation-duration: 18s;
    }
    
    .star8 {
        width: 60px;
        height: 60px;
        top: 5%;
        left: 12%;
        animation-name: twinkle;
        animation-duration: 3s;
    }
    
    .spark {
        width: 45px;
        height: 45px;
        top: 30%;
        right: 20%;
        animation-name: sparkle;
        animation-duration: 2s;
    }
    
    .spiral-galaxy {
        width: 180px;
        height: 180px;
        bottom: 5%;
        left: 2%;
        animation-name: rotate;
        animation-duration: 40s;
    }
    
    .orbit-rings {
        width: 220px;
        height: 220px;
        bottom: 15%;
        right: 2%;
        animation-name: orbitRings;
        animation-duration: 35s;
    }
    
    .planet-ring {
        width: 150px;
        height: 150px;
        top: 40%;
        left: 0%;
        animation-name: rotate;
        animation-duration: 22s;
    }
    
    /* Animation keyframes */
    @keyframes orbit {
        0% { transform: translate(0, 0) rotate(0deg); }
        25% { transform: translate(80px, -50px) rotate(90deg); }
        50% { transform: translate(150px, 0) rotate(180deg); }
        75% { transform: translate(80px, 50px) rotate(270deg); }
        100% { transform: translate(0, 0) rotate(360deg); }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px) rotate(0deg); }
        33% { transform: translateY(-40px) rotate(120deg); }
        66% { transform: translateY(20px) rotate(240deg); }
    }
    
    @keyframes drift {
        0% { transform: translateX(0px) translateY(0px); }
        25% { transform: translateX(60px) translateY(-30px); }
        50% { transform: translateX(120px) translateY(0px); }
        75% { transform: translateX(60px) translateY(30px); }
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
        0% { transform: rotate(0deg) scale(1) translate(0, 0); }
        25% { transform: rotate(90deg) scale(1.1) translate(40px, -20px); }
        50% { transform: rotate(180deg) scale(1.2) translate(80px, 0); }
        75% { transform: rotate(270deg) scale(1.1) translate(40px, 20px); }
        100% { transform: rotate(360deg) scale(1) translate(0, 0); }
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
st.markdown('<h1>Real-Time Race Strategy Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p class="subtitle">Simulating live race telemetry and pit strategy logic.</p>', unsafe_allow_html=True)

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

    # Video placeholder (bigger and square: equal width/height)
    st.markdown('<div class="panel"><div class="panel-title">LIVE CAMERA</div><div class="panel-placeholder" style="min-height:300px; aspect-ratio: 1 / 1;"></div></div>', unsafe_allow_html=True)

with center_col:
    # Car visualization from Elements folder
    render_car_panel()

    # Engine and Fuel panels under the car image (side-by-side like reference)
    ef1, ef2 = st.columns(2)
    with ef1:
        st.markdown('<div class="panel"><div class="panel-title">ENGINE TEMP (C)</div><div class="panel-placeholder" style="min-height:100px;"></div></div>', unsafe_allow_html=True)
    with ef2:
        st.markdown('<div class="panel"><div class="panel-title">FUEL (%)</div><div class="panel-placeholder" style="min-height:100px;"></div></div>', unsafe_allow_html=True)

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
        # Strategy decision
    decision, color = get_decision(tire_wear, lap_delta)
    decision_card.markdown(
                f"""
                <div class="decision-card">
                        <h2 style="color:white; font-family: 'Orbitron', monospace; margin-bottom: 1rem;">{decision}</h2>
                        <p style="color:#f1faee; font-size: 1.1rem; margin: 0.5rem 0;">Lap: {lap}</p>
                        <p style="color:#a8dadc; font-size: 1rem; margin: 0.5rem 0;">Tire Wear: {tire_wear:.1f}%</p>
                        <p style="color:#a8dadc; font-size: 1rem; margin: 0.5rem 0;">Fuel: {fuel:.1f}%</p>
                </div>
                """,
                unsafe_allow_html=True
        )

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
