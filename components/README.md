# Components

This folder contains modular components for the Race Strategy Dashboard. Each component is responsible for a specific visualization or feature.

## Components

### `track_visualization.py`
Handles the track visualization showing the car's position on the circuit.

**Functions:**
- `create_track_plot(lap, laps, radius)`: Creates a Plotly figure showing the track and car position
- `render_track_panel()`: Renders the complete track visualization panel with title

### `car_visualization.py`
Manages the car image display with interactive tire hotspots.

**Functions:**
- `create_car_css()`: Returns CSS styles specific to car visualization
- `render_car_visualization()`: Renders the car image with tire hotspots
- `render_car_panel()`: Renders the complete car visualization panel
- `get_image_base64(image_path)`: Helper function to encode images to base64

## Usage

Import components in your main application:

```python
from components import create_track_plot, render_track_panel, render_car_panel
```

## Benefits of This Organization

1. **Separation of Concerns**: Each component handles its own logic and styling
2. **Reusability**: Components can be easily reused in different parts of the application
3. **Maintainability**: Changes to specific features are isolated to their respective components
4. **Testability**: Each component can be tested independently
5. **Cleaner Main App**: The main app.py file is now focused on orchestration rather than implementation details
