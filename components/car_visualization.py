import streamlit as st
import base64
from pathlib import Path

def get_image_base64(image_path):
    """Encode image to base64 for embedding in HTML."""
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()

def create_car_css():
    """
    Create CSS styles for the car visualization component.
    """
    return """
    <style>
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
        transition: all 0.3s ease;
        transform-style: preserve-3d;
    }
    .car-frame:hover {
        box-shadow: inset 0 0 24px rgba(138,70,210,0.25), 0 15px 35px rgba(138,70,210,0.3), 0 0 30px rgba(138,70,210,0.2);
        border-color: rgba(138, 70, 210, 0.45);
    }
    .car-img { 
        width: 100%; 
        height: auto; 
        object-fit: contain; 
        display: block; 
        max-height: 56vh; 
        transition: all 0.3s ease;
    }
    .car-img:hover {
        filter: brightness(1.1) drop-shadow(0 10px 20px rgba(138, 70, 210, 0.4));
    }

    /* Reduce padding only for the car's panel wrapper */
    .panel-car { padding: 0.35rem 0.5rem; }

    /* Hotspot overlay on car image */
    .hotspot { position: absolute; border-radius: 50%; border: 2px solid rgba(138,70,210,0.55); background: rgba(138,70,210,0.12); cursor: help; backdrop-filter: blur(1px); }
    .hotspot:hover { box-shadow: 0 0 12px rgba(138,70,210,0.6); }
    .hotspot .tooltip { position: absolute; left: 50%; top: -12px; transform: translate(-50%, -100%); background: rgba(10,10,30,0.9); color: #e4d9ff; padding: 6px 10px; border-radius: 8px; font-family: 'Orbitron', monospace; font-size: 12px; white-space: nowrap; opacity: 0; pointer-events: none; border: 1px solid rgba(138,70,210,0.5); }
    .hotspot:hover .tooltip { opacity: 1; }
    /* Tire hotspot positions (tuned for Elements/Car.png) */
    .hotspot-fr { width: 9%; aspect-ratio: 1 / 1; top: 15%; right: 24%; }
    .hotspot-fl { width: 9%; aspect-ratio: 1 / 1; top: 15%; left: 24%; }
    .hotspot-rr { width: 9%; aspect-ratio: 1 / 1; bottom: 18%; right: 24%; }
    .hotspot-rl { width: 9%; aspect-ratio: 1 / 1; bottom: 18%; left: 24%; }
    </style>
    """

def render_car_visualization():
    """
    Render the car visualization with hotspots for tire monitoring.
    
    Returns:
        HTML string for the car visualization
    """
    # Apply car-specific CSS
    st.markdown(create_car_css(), unsafe_allow_html=True)
    
    # Find car image
    car_path = Path("Elements") / "Car.png"
    if not car_path.exists():
        alt_path = Path("Elements") / "HackTX F-1 Car-Photoroom.png"
        if alt_path.exists():
            car_path = alt_path
    
    if car_path.exists():
        car_b64 = get_image_base64(car_path)
        return f'''
        <div class="car-frame">
            <img class="car-img" src="data:image/png;base64,{car_b64}" alt="car"/>
            <div class="hotspot hotspot-fl"><div class="tooltip">Front Left Tire</div></div>
            <div class="hotspot hotspot-fr"><div class="tooltip">Front Right Tire</div></div>
            <div class="hotspot hotspot-rl"><div class="tooltip">Rear Left Tire</div></div>
            <div class="hotspot hotspot-rr"><div class="tooltip">Rear Right Tire</div></div>
        </div>
        '''
    else:
        return '<div class="panel-placeholder" style="min-height:420px;"></div>'

def render_car_panel():
    """
    Render the complete car visualization panel.
    """
    st.markdown('<div class="panel panel-car">', unsafe_allow_html=True)
    
    car_html = render_car_visualization()
    st.markdown(car_html, unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)
