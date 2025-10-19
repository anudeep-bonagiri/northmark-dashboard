# Lyra – Real-Time Race Strategy Dashboard

## Inspiration
Formula 1 decisions happen in milliseconds, but engineers and fans rarely see those choices unfold in real time. Lyra brings that experience to life. It combines live telemetry, AI strategy analysis, and realistic visuals into a single, immersive dashboard.

## What It Does
Lyra helps you watch, analyze, and act on race data as it happens.

- Live Track Visualization using the Circuit of the Americas
- AI Commentary powered by Google Gemini and ElevenLabs
- Real-Time Analytics for lap times, tire wear, fuel, and weather
- Strategy Engine that recommends pit stops or staying out
- Dynamic Charts showing lap trends and race metrics
- F1-Themed UI with responsive design and clean visuals

## How We Built It
<img width="1512" height="982" alt="Screenshot 2025-10-19 at 8 48 01 AM" src="https://github.com/user-attachments/assets/ead21fe3-67b0-4647-9619-20f7af75dd41" />
Stack:
- Streamlit for interactive front end
- Plotly for dynamic data visualization
- Google Gemini API for real-time AI insights
- ElevenLabs API for natural-sounding voice output
- Python + Pandas for data handling and simulation
- Custom CSS for F1-inspired interface design

Key Files:
- app.py – Main controller
- components/track_visualization.py – Renders COTA track and car motion
- components/car_visualization.py – Tire and damage displays
- ai_commentary.py – Gemini + ElevenLabs commentary module

## Challenges
- Maintaining Streamlit session state across updates
- Creating smooth car motion around the track
- Syncing Gemini text with ElevenLabs audio
- Handling concurrent live data streams
- Keeping visuals consistent with the F1 aesthetic

## Accomplishments
- Functional AI commentary system
- Modular visualization and UI components
- Realistic race simulation with lap tracking
- Smart pit-decision engine with visual alerts
- Clean, professional dashboard interface

## What We Learned
- Managing Streamlit state for live updates
- Integrating multiple APIs efficiently
- Translating telemetry into strategic visuals
- Building data-driven, human-centered interfaces
- Designing for real-time analytics

## Next Steps

Short Term:
- Connect to official F1 telemetry feeds
- Add multi-car visualization
- Build predictive analytics using ML models
- Optimize performance for mobile

Long Term:
- Add VR and AR racing modes
- Enable multiplayer strategy simulations
- Integrate race playback and analysis
- Support user-generated data and custom tracks
- Deploy scalable live-stream architecture with WebSockets

## Summary
Lyra turns race data into strategic intelligence.
It’s not just a dashboard. It’s how you see every decision happen in real time.
