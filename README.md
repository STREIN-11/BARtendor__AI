# AI Bartender Model

## Setup

1. Install dependencies:
```
pip install -r requirements.txt
```

2. Run the application:
```
python bartender_ai.py
```

3. Build EXE:
```
build_exe.bat
```
The EXE will be in `dist/BartenderAI.exe`

## API Endpoints (Port 5000)

### Start Camera Detection
```
POST http://localhost:5000/start
```

### Stop Camera Detection
```
POST http://localhost:5000/stop
```

### Chat with Bartender
```
POST http://localhost:5000/chat
Content-Type: application/json

{
  "message": "Can I get a whiskey?"
}
```

Response:
```json
{
  "response": "Coming right up, handsome! One whiskey for you.",
  "audio_file": "response.mp3",
  "greeting": "Good evening"
}
```

### Reset Conversation
```
POST http://localhost:5000/reset
```

## Features

- Camera detects person and greets automatically
- Time-based greetings (morning/afternoon/evening)
- Female bartender personality (Ava voice)
- Two audio files: `greeting.mp3` and `response.mp3` (both overwrite)
- Conversation history maintained
- REST API for integration

## Postman Testing

1. Start camera: POST to `/start`
2. Camera detects face → auto greets → `greeting.mp3` created
3. Manual chat: POST to `/chat` with JSON body (no name needed)
4. Audio files: `greeting.mp3` and `response.mp3` in `voice/` folder
