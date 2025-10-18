import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go
import base64
from pathlib import Path

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
    .background-elements {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        z-index: -1;
        pointer-events: none;
    }
    
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

    /* Car frame styling */
    .car-frame {
        position: relative;
        border-radius: 14px;
        padding: 4px; /* tighter frame so it hugs PNG better */
        background: linear-gradient(180deg, rgba(106,49,160,0.16), rgba(25,25,112,0.12));
        border: 2px solid rgba(138, 70, 210, 0.28);
        box-shadow: inset 0 0 24px rgba(138,70,210,0.18), 0 10px 28px rgba(0,0,0,0.34);
        min-height: 56vh; /* make panel longer */
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .car-img { width: 100%; height: auto; object-fit: contain; display: block; max-height: 56vh; }

    /* Reduce padding only for the car's panel wrapper */
    .panel-car { padding: 0.35rem 0.5rem; }

    /* Hotspot overlay on car image */
    .hotspot { position: absolute; border-radius: 50%; border: 2px solid rgba(138,70,210,0.55); background: rgba(138,70,210,0.12); cursor: help; backdrop-filter: blur(1px); }
    .hotspot:hover { box-shadow: 0 0 12px rgba(138,70,210,0.6); }
    .hotspot .tooltip { position: absolute; left: 50%; top: -12px; transform: translate(-50%, -100%); background: rgba(10,10,30,0.9); color: #e4d9ff; padding: 6px 10px; border-radius: 8px; font-family: 'Orbitron', monospace; font-size: 12px; white-space: nowrap; opacity: 0; pointer-events: none; border: 1px solid rgba(138,70,210,0.5); }
    .hotspot:hover .tooltip { opacity: 1; }
    /* Tire hotspot positions (tuned for Elements/Car.png) */
    .hotspot-fr { width: 14%; aspect-ratio: 1 / 1; top: 7%; right: 23%; }
    .hotspot-fl { width: 14%; aspect-ratio: 1 / 1; top: 7%; left: 23%; }
    .hotspot-rr { width: 14%; aspect-ratio: 1 / 1; bottom: 12%; right: 23%; }
    .hotspot-rl { width: 14%; aspect-ratio: 1 / 1; bottom: 12%; left: 23%; }
    
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
    st.markdown('<div class="panel"><div class="panel-title">RACE STATUS</div>', unsafe_allow_html=True)
    track_plot = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)

    # Video placeholder (bigger and square: equal width/height)
    st.markdown('<div class="panel"><div class="panel-title">LIVE CAMERA</div><div class="panel-placeholder" style="min-height:300px; aspect-ratio: 1 / 1;"></div></div>', unsafe_allow_html=True)

with center_col:
    # Car visualization from Elements folder
    st.markdown('<div class="panel panel-car">', unsafe_allow_html=True)
    car_path = Path("Elements") / "Car.png"
    if not car_path.exists():
        alt_path = Path("Elements") / "HackTX F-1 Car-Photoroom.png"
        if alt_path.exists():
            car_path = alt_path
    if car_path.exists():
        car_b64 = get_image_base64(car_path)
        st.markdown(
            f'''
            <div class="car-frame">
                <img class="car-img" src="data:image/png;base64,{car_b64}" alt="car"/>
                <div class="hotspot hotspot-fl"><div class="tooltip">Front Left Tire</div></div>
                <div class="hotspot hotspot-fr"><div class="tooltip">Front Right Tire</div></div>
                <div class="hotspot hotspot-rl"><div class="tooltip">Rear Left Tire</div></div>
                <div class="hotspot hotspot-rr"><div class="tooltip">Rear Right Tire</div></div>
            </div>
            ''',
            unsafe_allow_html=True,
        )
    else:
        st.markdown('<div class="panel-placeholder" style="min-height:420px;"></div>', unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

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
    st.markdown('<div class="panel"><div class="panel-title">WEATHER</div><div class="panel-placeholder" style="min-height:120px;"></div></div>', unsafe_allow_html=True)


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

    # Compute position (simulate car moving in circle)
    angle = (lap / laps) * 2 * np.pi
    x = np.cos(angle) * radius
    y = np.sin(angle) * radius

    # Track plot
    theta = np.linspace(0, 2 * np.pi, 200)
    track_x = np.cos(theta) * radius
    track_y = np.sin(theta) * radius

    fig = go.Figure()
    fig.add_trace(go.Scatter(x=track_x, y=track_y, mode="lines", line=dict(color="#4ecdc4", width=3), name="Track"))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", marker=dict(size=25, color="#ff6b6b", line=dict(width=2, color="white")), name="Car"))
    fig.update_layout(
        height=260, 
        margin=dict(l=10, r=10, t=10, b=10), 
        xaxis=dict(visible=False), 
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Orbitron, monospace", color="#f1faee")
    )
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

    time.sleep(update_interval)
