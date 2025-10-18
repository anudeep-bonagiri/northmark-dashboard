import streamlit as st
import pandas as pd
import numpy as np
import time
import plotly.graph_objects as go

# Page setup
st.set_page_config(page_title="Race Strategy Dashboard", layout="wide")

st.title("Real-Time Race Strategy Dashboard")
st.markdown("Simulating live race telemetry and pit strategy logic.")

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

# Stream containers
col1, col2 = st.columns([1.5, 1])

with col1:
    st.subheader("Track View")
    track_plot = st.empty()

with col2:
    st.subheader("Telemetry & Strategy")
    lap_chart = st.empty()
    decision_card = st.empty()

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
    fig.add_trace(go.Scatter(x=track_x, y=track_y, mode="lines", line=dict(color="gray"), name="Track"))
    fig.add_trace(go.Scatter(x=[x], y=[y], mode="markers", marker=dict(size=20, color="red"), name="Car"))
    fig.update_layout(height=400, margin=dict(l=10, r=10, t=10, b=10), xaxis=dict(visible=False), yaxis=dict(visible=False))
    track_plot.plotly_chart(fig, use_container_width=True)

    # Lap time trend
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(x=df["lap"][:i+1], y=df["lap_time"][:i+1], mode="lines+markers", name="Lap Time"))
    fig2.update_layout(yaxis_title="Lap Time (s)", xaxis_title="Lap", height=300)
    lap_chart.plotly_chart(fig2, use_container_width=True)

    # Strategy decision
    decision, color = get_decision(tire_wear, lap_delta)
    decision_card.markdown(
        f"""
        <div style="background-color:{color};padding:20px;border-radius:10px;text-align:center">
            <h2 style="color:white;">{decision}</h2>
            <p style="color:white;">Lap: {lap} | Tire Wear: {tire_wear:.1f}% | Fuel: {fuel:.1f}%</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    time.sleep(update_interval)
