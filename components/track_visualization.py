import streamlit as st
import plotly.graph_objects as go
import numpy as np

def create_track_plot(lap, laps, radius=100):
    """
    Create a realistic F1-style track visualization with turns and optimal racing line.
    
    Args:
        lap: Current lap number
        laps: Total number of laps
        radius: Track radius (not used for new track)
    
    Returns:
        Plotly figure object
    """
    # Create a simple, compact F1-style track layout matching the image
    def create_track_layout():
        """Create a smooth Circuit of the Americas-style circular track layout."""
        # Define the angular path for a looping track with varied turns
        theta = np.linspace(0, 2 * np.pi, 600)

        # Base radius variation to create a more dynamic track
        r = 100 + 10 * np.sin(3 * theta) + 5 * np.sin(6 * theta)

        # Convert polar to cartesian
        x = r * np.cos(theta)
        y = r * np.sin(theta)

        # Add "COTA-like" character: tighter esses and long straight
        # Create an S-section between angles 0.3π to 0.7π
        mask = (theta > 0.3 * np.pi) & (theta < 0.7 * np.pi)
        y[mask] += 25 * np.sin(8 * theta[mask])

        # Simulate a long straight at the back of the circuit
        mask_straight = (theta > 1.1 * np.pi) & (theta < 1.4 * np.pi)
        x[mask_straight] = np.linspace(80, -80, mask_straight.sum())

        # Close the loop cleanly
        x[-1] = x[0]
        y[-1] = y[0]

        return x, y

    
    def create_optimal_racing_line(track_x, track_y):
        """Create an optimal racing line that follows the track geometry accurately"""
        racing_line_x = []
        racing_line_y = []
        
        # Smooth the track first for better racing line calculation
        from scipy.ndimage import gaussian_filter1d
        
        # Apply smoothing to get better derivatives
        smooth_x = gaussian_filter1d(track_x, sigma=2)
        smooth_y = gaussian_filter1d(track_y, sigma=2)
        
        for i in range(len(smooth_x)):
            # Calculate tangent vector (direction of track)
            if i < len(smooth_x) - 1:
                dx = smooth_x[i+1] - smooth_x[i]
                dy = smooth_y[i+1] - smooth_y[i]
            else:
                dx = smooth_x[0] - smooth_x[i]
                dy = smooth_y[0] - smooth_y[i]
            
            # Calculate normal vector (perpendicular to track direction)
            length = np.sqrt(dx**2 + dy**2)
            if length > 0:
                # Normal vector (rotated 90 degrees)
                nx = -dy / length
                ny = dx / length
                
                # Dynamic offset based on track curvature
                # In turns, stay closer to the inside; on straights, use more of the track
                curvature = abs(dx * dy) / (length + 1e-6)  # Simple curvature measure
                base_offset = 6  # Base offset for track width
                dynamic_offset = base_offset * (1 - 0.3 * curvature)  # Reduce offset in turns
                
                racing_line_x.append(smooth_x[i] + nx * dynamic_offset)
                racing_line_y.append(smooth_y[i] + ny * dynamic_offset)
            else:
                racing_line_x.append(smooth_x[i])
                racing_line_y.append(smooth_y[i])
        
        return racing_line_x, racing_line_y
    
    def get_car_position(lap, laps, track_x, track_y):
        """Get car position along the track with smooth movement"""
        # Calculate position along track
        progress = (lap % laps) / laps if laps > 0 else 0
        total_points = len(track_x)
        
        # Use interpolation for smoother movement
        position_index = progress * (total_points - 1)
        
        # Handle wrapping around the track
        if position_index >= total_points:
            position_index = position_index % total_points
        
        # Get the exact position (can be fractional)
        if position_index < total_points - 1:
            # Interpolate between two points for smoother movement
            idx1 = int(position_index)
            idx2 = idx1 + 1
            frac = position_index - idx1
            
            x = track_x[idx1] + frac * (track_x[idx2] - track_x[idx1])
            y = track_y[idx1] + frac * (track_y[idx2] - track_y[idx1])
        else:
            # Handle the case where we're at the end
            x = track_x[-1]
            y = track_y[-1]
        
        return x, y
    
    # Create track layout
    track_x, track_y = create_track_layout()
    racing_line_x, racing_line_y = create_optimal_racing_line(track_x, track_y)
    
    # Get car position
    car_x, car_y = get_car_position(lap, laps, track_x, track_y)
    
    # Create the plot
    fig = go.Figure()
    
    # Add track outline (thicker)
    fig.add_trace(go.Scatter(
        x=track_x, 
        y=track_y, 
        mode="lines", 
        line=dict(color="#4ecdc4", width=8), 
        name="Track",
        hovertemplate="Track Edge<br>%{x:.1f}, %{y:.1f}<extra></extra>"
    ))
    
    # Add optimal racing line (thicker and more visible)
    fig.add_trace(go.Scatter(
        x=racing_line_x, 
        y=racing_line_y, 
        mode="lines", 
        line=dict(color="#ff6b6b", width=4, dash="dot"), 
        name="Optimal Line",
        hovertemplate="Racing Line<br>%{x:.1f}, %{y:.1f}<extra></extra>"
    ))
    
    # Add car position
    fig.add_trace(go.Scatter(
        x=[car_x], 
        y=[car_y], 
        mode="markers", 
        marker=dict(
            size=20, 
            color="#ff6b6b", 
            line=dict(width=3, color="white"),
            symbol="circle"
        ), 
        name="Car",
        hovertemplate="Car Position<br>Lap: %{text}<extra></extra>",
        text=[f"{lap}"]
    ))
    
    # Add track sectors with proper colors (matching the image)
    # Sector 1 (Red) - Turns 1-5
    sector1_x = track_x[:150]  # First 150 points
    sector1_y = track_y[:150]
    fig.add_trace(go.Scatter(
        x=sector1_x,
        y=sector1_y,
        mode="lines",
        line=dict(color="#ff6b6b", width=6),
        name="Sector 1",
        showlegend=True,
        hoverinfo="skip"
    ))
    
    # Sector 2 (Blue) - Turns 6-11
    sector2_x = track_x[150:300]  # Middle section
    sector2_y = track_y[150:300]
    fig.add_trace(go.Scatter(
        x=sector2_x,
        y=sector2_y,
        mode="lines",
        line=dict(color="#4ecdc4", width=6),
        name="Sector 2",
        showlegend=True,
        hoverinfo="skip"
    ))
    
    # Sector 3 (Yellow) - Turns 12-20
    sector3_x = track_x[300:]  # Final section
    sector3_y = track_y[300:]
    fig.add_trace(go.Scatter(
        x=sector3_x,
        y=sector3_y,
        mode="lines",
        line=dict(color="#f1c40f", width=6),
        name="Sector 3",
        showlegend=True,
        hoverinfo="skip"
    ))
    
    # Add DRS Detection Zones
    # DRS Detection Zone 1 (before Turn 11)
    drs1_x = [0, 5, 5, 0, 0]
    drs1_y = [58, 58, 62, 62, 58]
    fig.add_trace(go.Scatter(
        x=drs1_x,
        y=drs1_y,
        mode="lines",
        line=dict(color="#00ff00", width=3),
        fill="toself",
        fillcolor="rgba(0, 255, 0, 0.3)",
        name="DRS Detection 1",
        showlegend=True,
        hoverinfo="skip"
    ))
    
    # DRS Detection Zone 2 (before Turn 19)
    drs2_x = [-2, 2, 2, -2, -2]
    drs2_y = [62, 62, 65, 65, 62]
    fig.add_trace(go.Scatter(
        x=drs2_x,
        y=drs2_y,
        mode="lines",
        line=dict(color="#00ff00", width=3),
        fill="toself",
        fillcolor="rgba(0, 255, 0, 0.3)",
        name="DRS Detection 2",
        showlegend=True,
        hoverinfo="skip"
    ))
    
    # Add Speed Trap
    speed_trap_x = [-10, -5, -5, -10, -10]
    speed_trap_y = [55, 55, 58, 58, 55]
    fig.add_trace(go.Scatter(
        x=speed_trap_x,
        y=speed_trap_y,
        mode="lines",
        line=dict(color="#ff00ff", width=3),
        fill="toself",
        fillcolor="rgba(255, 0, 255, 0.3)",
        name="Speed Trap",
        showlegend=True,
        hoverinfo="skip"
    ))
    
    # Update layout to accommodate the closed circuit
    fig.update_layout(
    height=600,
    margin=dict(l=10, r=10, t=10, b=10),
    xaxis=dict(visible=False, range=[-130, 130]),
    yaxis=dict(visible=False, range=[-130, 130]),
    plot_bgcolor='rgba(0,0,0,0)',
    paper_bgcolor='rgba(0,0,0,0)',
    font=dict(family="Orbitron, monospace", color="#f1faee"),
    showlegend=True,
    legend=dict(
        orientation="h",
        yanchor="bottom",
        y=1.02,
        xanchor="right",
        x=1
    )
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