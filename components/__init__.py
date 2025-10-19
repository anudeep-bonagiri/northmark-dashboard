"""
Components package for the Race Strategy Dashboard.

This package contains modular components for different visualization features:
- track_visualization: Track and car position visualization
- car_visualization: Car image with interactive tire hotspots
"""

from .track_visualization import create_track_plot, render_track_panel
from .car_visualization import render_car_visualization, render_car_panel

__all__ = [
    'create_track_plot',
    'render_track_panel', 
    'render_car_visualization',
    'render_car_panel'
]
