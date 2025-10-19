import os
import json
import requests
import base64
import io
from typing import Dict, Any, Optional
import streamlit as st
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class AICommentarySystem:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        self.elevenlabs_api_key = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")  # Default voice
        
    def generate_commentary(self, race_stats: Dict[str, Any]) -> str:
        """Generate race commentary using Gemini AI"""
        if not self.gemini_api_key:
            return "Gemini API key not configured"
            
        # Prepare the prompt for Gemini
        prompt = f"""
        You are a Formula 1 Pit Stop Director and Race Strategist. Analyze the current race situation and provide 
        strategic updates on what's happening and what's coming next. Give tactical insights and predictions.
        
        Current Race Data:
        - Lap: {race_stats.get('lap', 'N/A')}
        - Lap Time: {race_stats.get('lap_time', 0):.2f}s
        - Tire Wear: {race_stats.get('tire_wear', 0):.1f}%
        - Fuel Level: {race_stats.get('fuel', 0):.1f}%
        - Strategy Decision: {race_stats.get('decision', 'N/A')}
        - Weather: {race_stats.get('weather', 0):.1f}°C
        
        As a pit stop director, analyze:
        1. Current performance vs previous laps
        2. Tire degradation and when we'll need to pit
        3. Fuel consumption and strategy implications
        4. What the next few laps will look like
        5. Strategic recommendations for the team
        
        Speak like a professional race strategist giving a tactical briefing. Be analytical, forward-thinking, 
        and focus on strategy and upcoming decisions. Keep it to 2-3 sentences but make it insightful and strategic.
        """
        
        try:
            # Call Gemini API
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={self.gemini_api_key}"
            
            payload = {
                "contents": [{
                    "parts": [{"text": prompt}]
                }]
            }
            
            headers = {"Content-Type": "application/json"}
            response = requests.post(url, json=payload, headers=headers)
            
            if response.status_code == 200:
                result = response.json()
                commentary = result['candidates'][0]['content']['parts'][0]['text']
                return commentary.strip()
            else:
                return f"Error generating commentary: {response.status_code}"
                
        except Exception as e:
            return f"Error calling Gemini API: {str(e)}"
    
    def text_to_speech(self, text: str) -> Optional[bytes]:
        """Convert text to speech using Eleven Labs"""
        if not self.elevenlabs_api_key:
            st.error("Eleven Labs API key not configured")
            return None
            
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice_id}"
            
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_api_key
            }
            
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                st.error(f"❌ Eleven Labs API error: {response.status_code}")
                return None
                
        except Exception as e:
            st.error(f"❌ Error calling Eleven Labs API: {str(e)}")
            return None
    
    def generate_and_speak(self, race_stats: Dict[str, Any]) -> Optional[bytes]:
        """Generate commentary and convert to speech"""
        commentary = self.generate_commentary(race_stats)
        if commentary and not commentary.startswith("Error"):
            return self.text_to_speech(commentary)
        else:
            st.error(f"❌ Commentary generation failed")
            return None

def create_commentary_interface():
    """Create Streamlit interface for AI commentary"""
    
    # Check if API keys are configured
    gemini_key = os.getenv("GEMINI_API_KEY")
    elevenlabs_key = os.getenv("ELEVENLABS_API_KEY")
    voice_id = os.getenv("ELEVENLABS_VOICE_ID", "pNInz6obpgDQGcFmaJgB")
    
    if not gemini_key or gemini_key == "your_gemini_api_key_here":
        st.warning("⚠️ Gemini API key not configured. Please update your `.env` file.")
        st.markdown("**Setup Instructions:**")
        st.markdown("1. Open the `.env` file in your project root")
        st.markdown("2. Replace `your_gemini_api_key_here` with your actual Gemini API key")
        st.markdown("3. Get your key from: [Google AI Studio](https://makersuite.google.com/app/apikey)")
    
    if not elevenlabs_key or elevenlabs_key == "your_elevenlabs_api_key_here":
        st.warning("⚠️ Eleven Labs API key not configured. Please update your `.env` file.")
        st.markdown("**Setup Instructions:**")
        st.markdown("1. Open the `.env` file in your project root")
        st.markdown("2. Replace `your_elevenlabs_api_key_here` with your actual Eleven Labs API key")
        st.markdown("3. Get your key from: [Eleven Labs](https://elevenlabs.io/)")
    
    
    return gemini_key, elevenlabs_key, voice_id

def play_audio(audio_bytes: bytes):
    """Play audio in Streamlit"""
    if audio_bytes:
        audio_base64 = base64.b64encode(audio_bytes).decode()
        st.audio(f"data:audio/mpeg;base64,{audio_base64}", format="audio/mpeg", autoplay=True)
