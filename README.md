# Alfred Gemini

**Voice assistant powered by Google AI with Felix Dennis energy.**

Blunt. Street-smart. No bullshit.

## Features

- **Voice interaction** - Speak naturally, get spoken responses
- **Gemini Pro/Flash** - Google's latest AI models
- **Alfred personality** - Direct, actionable advice with Rule + Next format
- **Fast mode** - Low-latency responses for quick queries
- **Text mode** - Type instead of talk when needed

## Quick Start

### 1. Install dependencies

```bash
cd alfredgemini
python3 -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Set up API key

```bash
cp .env.example .env
# Edit .env and add your Google AI API key
# Get one at: https://aistudio.google.com/app/apikey
```

### 3. Run Alfred

```bash
# Voice mode (default)
python main.py

# Text-only mode
python main.py --text

# Continuous listening
python main.py --continuous

# Quick test
python main.py --test
```

## Usage

### Voice Mode
```
🎤 Speak after Alfred's greeting
🎩 Alfred responds with voice
```

### Text Mode
```
👤 You: What should I focus on today?
🎩 Alfred: [response with bullets, Rule, Next]
```

## Project Structure

```
alfredgemini/
├── main.py              # Entry point
├── alfred/
│   ├── __init__.py
│   ├── config.py        # Configuration
│   ├── personality.py   # Alfred's voice contract
│   ├── brain.py         # Gemini AI integration
│   ├── voice_input.py   # Speech-to-text
│   ├── voice_output.py  # Text-to-speech
│   └── conversation.py  # Conversation state machine
├── requirements.txt
├── .env.example
└── README.md
```

## Alfred's Style

- **3-7 bullets** by default
- **Short punchy sentences** (10-15 words)
- **Ends with Rule + Next** for actionable topics
- **Pushes back** on bad ideas
- **No fluff**, no hedging, no corporate speak

### Example Response

```
👤 Should I quit my job to start a business?

🎩 Alfred:
- "Thinking about quitting" is the coward's phrase. Either you're
  building something nights and weekends, or you're daydreaming.
- The Slowlane trap: trading time for money at a job, wanting to
  trade time for money differently. That's not escape.
- Real question: 6 months runway + validated idea? Or just "passion"?

Rule: Don't quit your job. Make your job quit you.

Next:
1. Calculate monthly burn × 12 = runway target
2. Pick one problem to solve in 2 hrs/day after work
3. Get 3 paying customers before thinking about quitting
```

## Requirements

- Python 3.10+
- macOS/Linux (Windows with limitations)
- Google AI API key
- Microphone (for voice mode)

## API Keys

Get your API key from [Google AI Studio](https://aistudio.google.com/app/apikey).

## Web UI

The React web UI is in `index.tsx`. Run separately:

```bash
npm install
npm run dev
```

## License

MIT
