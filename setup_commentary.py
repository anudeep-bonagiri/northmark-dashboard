#!/usr/bin/env python3
"""
Setup script for AI Commentary System
This script helps configure the required API keys for Gemini and Eleven Labs
"""

import os
from dotenv import load_dotenv

def setup_api_keys():
    """Interactive setup for API keys"""
    print("🎙️ AI Commentary System Setup")
    print("=" * 40)
    
    # Load existing .env file if it exists
    load_dotenv()
    
    print("\n1. Gemini API Key Setup:")
    print("   - Go to: https://makersuite.google.com/app/apikey")
    print("   - Create a new API key")
    print("   - Copy the key and paste it below")
    
    gemini_key = input("\nEnter your Gemini API key: ").strip()
    
    print("\n2. Eleven Labs API Key Setup:")
    print("   - Go to: https://elevenlabs.io/")
    print("   - Sign up/login and go to your profile")
    print("   - Copy your API key")
    
    elevenlabs_key = input("\nEnter your Eleven Labs API key: ").strip()
    
    print("\n3. Eleven Labs Voice ID (optional):")
    print("   - Default voice ID: pNInz6obpgDQGcFmaJgB")
    print("   - You can find other voice IDs in your Eleven Labs dashboard")
    
    voice_id = input("\nEnter voice ID (or press Enter for default): ").strip()
    if not voice_id:
        voice_id = "pNInz6obpgDQGcFmaJgB"
    
    # Create .env file
    env_content = f"""# AI Commentary System API Keys
GEMINI_API_KEY={gemini_key}
ELEVENLABS_API_KEY={elevenlabs_key}
ELEVENLABS_VOICE_ID={voice_id}
"""
    
    with open('.env', 'w') as f:
        f.write(env_content)
    
    print(f"\n✅ API keys saved to .env file")
    print(f"✅ You can now run the dashboard with AI commentary!")
    
    # Test the setup
    print(f"\n🧪 Testing API connections...")
    
    try:
        from ai_commentary import AICommentarySystem
        system = AICommentarySystem()
        
        # Test commentary generation
        test_stats = {
            'lap': 1,
            'lap_time': 90.5,
            'tire_wear': 20.0,
            'fuel': 95.0,
            'decision': 'Stay Out',
            'weather': 22.0
        }
        
        commentary = system.generate_commentary(test_stats)
        if commentary and not commentary.startswith("Error"):
            print(f"✅ Gemini API working! Generated: {commentary[:50]}...")
        else:
            print(f"❌ Gemini API error: {commentary}")
            
    except Exception as e:
        print(f"❌ Setup test failed: {e}")
        print("   Make sure to install requirements: pip install -r requirements.txt")

if __name__ == "__main__":
    setup_api_keys()
