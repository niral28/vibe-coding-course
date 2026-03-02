# Example Projects 💡

This directory contains complete, working examples of projects built during the GSET Vibe Coding course. These serve as:
- **Reference implementations** for students
- **Inspiration** for final projects
- **Templates** for common patterns

---

## Projects

### 🎮 [Wordle Game Web](wordle-game-web/)
**Full-stack AI-powered Wordle game**

- Interactive web interface with vanilla JavaScript
- Backend powered by Google Gemini API
- Function calling for game logic validation
- Color-coded hint system (green/yellow/gray)
- Word validation from curated word list

**Tech Stack**: Python (Flask), JavaScript, HTML/CSS, Gemini API

**Key Learning**: Function calling, game state management, web APIs

---

### 🌐 [Web Browsing Agent](web-browsing-agent/)
**Voice-enabled AI agent that browses the web**

- Voice input using Web Speech API
- AI-powered web search and page summarization
- Text-to-speech audio responses
- Real-time interaction with streaming responses
- Function calling for web scraping

**Tech Stack**: Python (Flask), WebSockets, Gemini Live API, Web Speech API

**Key Learning**: Multi-modal AI, voice integration, real-time streaming

---

### 📋 [Project Templates](project-templates/)
**Starter templates for common project types**

Coming soon:
- `text-chatbot-template/` - Basic chatbot structure
- `image-generator-template/` - Image generation app
- `multimodal-app-template/` - Full-stack multi-modal app

---

## How to Use These Examples

1. **Explore the code**: Read through each project to understand the architecture
2. **Run locally**: Follow the README in each project directory
3. **Modify and extend**: Use as a starting point for your own ideas
4. **Learn patterns**: Notice common patterns like function calling, API integration, error handling

---

## Running an Example Project

```bash
# Navigate to project directory
cd example-projects/wordle-game-web

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp ../../shared/.env.example .env
# Edit .env with your API keys

# Run the application
python app.py

# Open browser to http://localhost:5000
```

---

## Contributing Your Project

Completed an awesome project? Share it with the class!

1. Create a new directory under `example-projects/`
2. Include:
   - All source code files
   - `requirements.txt` with dependencies
   - `README.md` with description and setup instructions
   - Screenshots or demo video (optional but encouraged)
3. Submit via pull request or share with instructor

---

## Project Ideas

Looking for inspiration? Consider these themes:

- **Screen Addiction**: Break reminder app, activity suggester
- **College Assistant**: Study scheduler, flashcard generator, paper summarizer
- **Sustainability**: Carbon footprint tracker, eco-tip generator
- **Mental Wellness**: Mood journal, breathing exercise guide, positive affirmations
- **Creative Expression**: Poetry generator, music lyric writer, art style transfer

---

## Resources

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [JavaScript Fetch API](https://developer.mozilla.org/en-US/docs/Web/API/Fetch_API)

---

**Ready to build?** Start with a template or dive into the examples! 🚀
