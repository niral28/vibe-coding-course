# Encyclopedia Web Agent

A web-based AI agent that searches Wikipedia to answer your questions, with full voice input/output capabilities inspired by Perplexity and Claude.com interfaces.

## Features

- 🔍 **Wikipedia Search**: Intelligent encyclopedia search using Gemini AI
- 🎤 **Voice Input**: Record questions using your microphone
- 🔊 **Voice Output**: Hear responses spoken aloud
- 💬 **Full Chat History**: See every conversation turn and tool call
- 🌐 **Modern Web Interface**: Beautiful, responsive design
- 🔄 **Real-time Processing**: Watch the AI think through search queries

## Setup

1. **Install Dependencies**:
   ```bash
   cd web_app
   pip install -r requirements.txt
   ```

2. **Environment Variables**:
   Create a `.env` file in the web_app directory:
   ```
   GEMINI_API_KEY=your_gemini_api_key_here
   ```

3. **Run the Application**:
   ```bash
   python app.py
   ```

4. **Open Browser**:
   Navigate to `http://localhost:5000`

## Usage

### Text Input
- Type your question in the input field
- Press Enter or click the send button
- Watch as the AI searches Wikipedia and provides detailed answers

### Voice Input
- Hold down the microphone button while speaking
- Release to stop recording
- The system will automatically transcribe and process your question
- Responses are played back as audio

### Chat History
- All conversation turns are displayed in the interface
- See tool calls and search queries used by the AI
- Start new chats to begin fresh conversations

## Architecture

### Backend (Flask)
- `app.py`: Main Flask application with API routes
- `/api/chat`: Process text/voice queries and return responses
- `/api/voice-to-text`: Convert audio recordings to text
- `/api/text-to-speech`: Generate speech from text responses

### Frontend
- `templates/index.html`: Main web interface
- `static/css/style.css`: Modern, responsive styling
- `static/js/app.js`: JavaScript handling voice recording and UI interactions

### AI Integration
- Uses existing `web_agent.py` logic for Wikipedia search
- Integrates `stt_web_tts.py` for voice capabilities
- Maintains full conversation context and tool calling

## Voice Requirements

### macOS
- Built-in microphone access via browser
- Uses `afplay` for audio output (built-in to macOS)
- Requires `sox` for audio recording: `brew install sox`

### Permissions
- Browser will request microphone permissions on first use
- Allow microphone access for voice functionality

## API Endpoints

- `GET /`: Main web interface
- `POST /api/chat`: Send queries and receive responses
- `POST /api/voice-to-text`: Upload audio for transcription
- `POST /api/text-to-speech`: Get audio response for text
- `GET /api/session/<id>`: Get specific chat session
- `GET /api/sessions`: List all chat sessions

## Development

The web app preserves all functionality from the original command-line agent while adding a modern web interface with full voice capabilities.