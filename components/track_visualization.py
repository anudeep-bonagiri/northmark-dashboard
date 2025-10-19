import streamlit as st
import plotly.graph_objects as go
import numpy as np

def create_track_plot(lap, laps, radius=100):
    """
    Create a track visualization showing the car's position.
    
    Args:
        lap: Current lap number
        laps: Total number of laps
        radius: Track radius
    
    Returns:
        Plotly figure object
    """
    # Compute position (simulate car moving in circle)
    angle = (lap / laps) * 2 * np.pi
    x = np.cos(angle) * radius
    y = np.sin(angle) * radius
    
    # Track plot
    theta = np.linspace(0, 2 * np.pi, 200)
    track_x = np.cos(theta) * radius
    track_y = np.sin(theta) * radius
    
    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=track_x, 
        y=track_y, 
        mode="lines", 
        line=dict(color="#4ecdc4", width=3), 
        name="Track"
    ))
    fig.add_trace(go.Scatter(
        x=[x], 
        y=[y], 
        mode="markers", 
        marker=dict(size=25, color="#ff6b6b", line=dict(width=2, color="white")), 
        name="Car"
    ))
    
    fig.update_layout(
        height=260, 
        margin=dict(l=10, r=10, t=10, b=10), 
        xaxis=dict(visible=False), 
        yaxis=dict(visible=False),
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(family="Orbitron, monospace", color="#f1faee")
    )
    
    return fig

def render_track_panel():
    """
    Render the track visualization panel with title.
    """
    st.markdown('<div class="panel"><div class="panel-title">RACE STATUS</div>', unsafe_allow_html=True)
    track_plot = st.empty()
    st.markdown('</div>', unsafe_allow_html=True)
    return track_plot
