# Wordle Game Web 🎮

An AI-powered implementation of the popular Wordle word-guessing game, using Google Gemini API for game logic and validation.

---

## Features

- ✅ **Interactive UI**: Responsive web interface with keyboard input
- ✅ **AI Game Master**: Gemini API validates guesses and provides hints
- ✅ **Color-Coded Feedback**: Green (correct), Yellow (wrong position), Gray (not in word)
- ✅ **Function Calling**: AI invokes game functions to check guesses
- ✅ **Word Validation**: 2,315 five-letter words from official Wordle list
- ✅ **Game State Management**: Tracks guesses, win/loss conditions

---

## How It Works

1. **User enters a 5-letter word** in the web interface
2. **Frontend sends guess** to Flask backend via API
3. **Backend uses Gemini API** with function calling to validate guess
4. **AI invokes `validate_word()` function** to check against secret word
5. **Returns color-coded hints** (green/yellow/gray for each letter)
6. **Game continues** until word is guessed or 6 attempts are used

---

## Tech Stack

- **Backend**: Python 3.11+, Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: Google Gemini API with function calling
- **API Integration**: RESTful endpoints

---

## Setup & Installation

1. **Navigate to project directory**
   ```bash
   cd example-projects/wordle-game-web
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   # Copy example env file
   cp ../../shared/.env.example .env

   # Edit .env and add your Gemini API key
   GEMINI_API_KEY=your_api_key_here
   ```

4. **Run the application**
   ```bash
   python app.py
   ```

5. **Open browser**
   ```
   http://localhost:5000
   ```

---

## File Structure

```
wordle-game-web/
├── app.py              # Flask backend with Gemini integration
├── index.html          # Game interface
├── script.js           # Frontend game logic
├── style.css           # Styling and animations
├── requirements.txt    # Python dependencies
└── README.md          # This file
```

---

## Key Code Concepts

### Function Calling Pattern
```python
tools = [
    {
        "function_declarations": [
            {
                "name": "validate_word",
                "description": "Validates user's guess in Wordle game",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "guess": {"type": "string", "description": "5-letter word guess"},
                        "secret_word": {"type": "string", "description": "The target word"}
                    }
                }
            }
        ]
    }
]
```

### Game Logic
- Exact match (same letter, same position) → **Green**
- Letter exists but wrong position → **Yellow**
- Letter not in word → **Gray**

---

## Customization Ideas

- [ ] Add difficulty levels (4-letter, 6-letter words)
- [ ] Implement streak tracking
- [ ] Add daily word challenge mode
- [ ] Include hints system (show one letter)
- [ ] Add multiplayer mode
- [ ] Integrate with user authentication
- [ ] Add sound effects and animations

---

## Troubleshooting

**Issue**: "API key not found"
- Make sure `.env` file exists and contains `GEMINI_API_KEY`

**Issue**: "Connection refused"
- Check if Flask server is running on port 5000
- Try a different port: `flask run --port 5001`

**Issue**: "Word not in list"
- Ensure you're using valid 5-letter English words
- Check the word list is loaded correctly

---

## Learn More

- [Gemini Function Calling Docs](https://ai.google.dev/docs/function_calling)
- [Flask Quickstart](https://flask.palletsprojects.com/quickstart/)
- [Original Wordle Game](https://www.nytimes.com/games/wordle)

---

**Built with** ❤️ **during GSET Vibe Coding Course**
