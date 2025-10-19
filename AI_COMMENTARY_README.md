# 🎙️ AI Commentary System

This system integrates **Gemini AI** and **Eleven Labs** to generate real-time race commentary based on telemetry data.

## Features

- **Real-time Commentary**: Generates commentary based on current race stats
- **Voice Synthesis**: Converts text to natural-sounding speech
- **Automatic Triggers**: Commentary plays during critical events (tire wear, fuel low, etc.)
- **Manual Control**: Button to generate commentary on demand

## Setup

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Get API Keys

#### Gemini API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key

#### Eleven Labs API Key
1. Go to [Eleven Labs](https://elevenlabs.io/)
2. Sign up/login
3. Go to your profile and copy your API key
4. Optionally, choose a voice ID from their voice library

### 3. Configure API Keys

#### Option A: Use Setup Script
```bash
python setup_commentary.py
```

#### Option B: Manual Configuration
Create a `.env` file in the project root:
```env
GEMINI_API_KEY=your_gemini_key_here
ELEVENLABS_API_KEY=your_elevenlabs_key_here
ELEVENLABS_VOICE_ID=pNInz6obpgDQGcFmaJgB
```

#### Option C: In-App Configuration
1. Run the dashboard: `streamlit run app.py`
2. Expand the "🔧 API Configuration" section
3. Enter your API keys
4. Click "Save API Keys"

## Usage

### Automatic Commentary
The system automatically generates commentary:
- Every 3 laps
- When tire wear > 60%
- When fuel < 20%
- During pit stops

### Manual Commentary
Click the "🎙️ Generate Live Commentary" button to generate commentary for the current race state.

### Customization

#### Change Commentary Frequency
Modify the trigger conditions in `app.py`:
```python
# Generate commentary every 3 laps or on critical events
if lap % 3 == 0 or tire_wear > 60 or fuel < 20:
    commentary_audio = commentary_system.generate_and_speak(race_stats)
```

#### Customize Commentary Style
Edit the prompt in `ai_commentary.py`:
```python
prompt = f"""
You are a professional Formula 1 race commentator...
# Modify this prompt to change commentary style
"""
```

#### Change Voice
Update the voice ID in your `.env` file or in the app configuration.

## API Costs

- **Gemini**: Free tier available, pay-per-use after limits
- **Eleven Labs**: Free tier includes 10,000 characters/month

## Troubleshooting

### Common Issues

1. **"Gemini API key not configured"**
   - Make sure your API key is set in `.env` or configured in the app
   - Verify the key is valid

2. **"Eleven Labs API error"**
   - Check your API key is correct
   - Ensure you have remaining credits

3. **No audio playing**
   - Check browser audio permissions
   - Verify the voice ID is valid

### Debug Mode
Add debug prints to see what's happening:
```python
print(f"Generated commentary: {commentary}")
print(f"Audio bytes length: {len(audio_bytes) if audio_bytes else 0}")
```

## Example Output

**Generated Commentary:**
> "The driver is maintaining excellent pace with a 92.3 second lap time. Tire wear is at 45% which is still manageable, but fuel levels are dropping to 78%. The strategy team is monitoring closely as we approach the pit window."

**Audio:** Natural-sounding speech with professional F1 commentator tone.

## Advanced Features

### Custom Race Events
Add custom commentary triggers:
```python
# Add to the simulation loop
if lap == 10:  # Special lap 10 commentary
    commentary_audio = commentary_system.generate_and_speak(race_stats)
```

### Multiple Voices
Use different voices for different types of commentary:
```python
# Use different voice for pit stop commentary
if decision == "PIT NOW":
    commentary_system.elevenlabs_voice_id = "different_voice_id"
```

### Commentary History
Store and replay previous commentary:
```python
commentary_history = []
commentary_history.append(commentary)
```
