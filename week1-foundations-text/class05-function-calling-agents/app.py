import os
import uuid
import json
from flask import Flask, render_template, request, jsonify, session
from flask_cors import CORS
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Import the core logic directly from the starter script to reuse existing code!
try:
    from wordle_agent_starter import (
        client,
        get_secret_word,
        validate_word,
        end_game,
        tools,
        MODEL,
        MAX_GUESSES
    )
except ImportError as e:
    print("Error importing wordle_agent_starter. Ensure you are running from the correct folder or the path is set up correctly.")
    raise e

app = Flask(__name__)
# Secure the session with a strong secret key
app.secret_key = os.environ.get("FLASK_SECRET_KEY", os.urandom(24).hex())
CORS(app)

# In-memory store for game sessions to avoid size limits on standard Flask cookie-based sessions.
# Maps game_id -> session state dictionary
GAMES = {}

def get_feedback_colors(guess, secret_word):
    """
    Computes a list of 5 colors ('correct', 'present', 'absent') representing 
    the Wordle grid tile colors. Matches the exact validate_word logic.
    """
    guess = guess.strip().upper()
    secret_word = secret_word.strip().upper()
    
    # Track which letters in the secret word have been matched
    # to handle duplicate letter edge cases correctly (Wordle standard).
    secret_letters_matched = [False] * 5
    colors = [None] * 5
    
    # First Pass: Check for green (correct spots)
    for i in range(5):
        if guess[i] == secret_word[i]:
            colors[i] = "correct"
            secret_letters_matched[i] = True
            
    # Second Pass: Check for yellow (present in word but wrong spot)
    for i in range(5):
        if colors[i] is not None:
            continue
            
        # Check if the letter exists in the secret word at an unmatched index
        found = False
        for j in range(5):
            if not secret_letters_matched[j] and secret_word[j] == guess[i]:
                secret_letters_matched[j] = True
                colors[i] = "present"
                found = True
                break
        if not found:
            colors[i] = "absent"
            
    return colors

@app.route("/")
def index():
    """Renders the main Wordle single-page web app."""
    return render_template("index.html")

@app.route("/api/new-game", methods=["POST"])
def new_game():
    """Starts a new Wordle game session and returns the initial state."""
    game_id = uuid.uuid4().hex
    secret_word = get_secret_word()
    
    # System prompt for the Gemini agent
    system_prompt = f"""
You are a Wordle game master.

The secret word is {secret_word}.
The player has {MAX_GUESSES} guesses.

For every player guess, call validate_word to check it.

Use the tool's feedback to respond to the player.

If the player guesses the secret word correctly, call:
end_game(reason="WON", answer="{secret_word}")

If the player runs out of guesses, call:
end_game(reason="LOST", answer="{secret_word}")

If the player quits, call:
end_game(reason="QUIT", answer="{secret_word}")
"""
    
    # Initialize session state for this game
    GAMES[game_id] = {
        "secret_word": secret_word,
        "guesses_used": 0,
        "game_over": False,
        "reason": None,
        "messages": [
            {"role": "system", "content": system_prompt}
        ],
        "guesses": [],  # list of {"word": "GUESS", "colors": [...]}
        "ai_messages": ["🟩 Welcome to AI Wordle! I'm thinking of a 5-letter word. Start by entering your first guess!"]
    }
    
    # Store game_id in cookie session
    session["game_id"] = game_id
    
    return jsonify({
        "status": "success",
        "guesses_used": 0,
        "max_guesses": MAX_GUESSES,
        "game_over": False,
        "ai_message": GAMES[game_id]["ai_messages"][-1]
    })

@app.route("/api/guess", methods=["POST"])
def submit_guess():
    """Processes a player's 5-letter guess through the Gemini agent loop."""
    game_id = session.get("game_id")
    if not game_id or game_id not in GAMES:
        return jsonify({"error": "Game session not found. Please start a new game."}), 400
        
    game = GAMES[game_id]
    if game["game_over"]:
        return jsonify({"error": "Game is already over.", "game_over": True}), 400
        
    data = request.json or {}
    guess = data.get("guess", "").strip().upper()
    
    if len(guess) != 5 or not guess.isalpha():
        return jsonify({"error": "Guess must be a 5-letter English word containing only letters."}), 400
        
    game["guesses_used"] += 1
    
    # Add player's guess to the Gemini chat history
    game["messages"].append({
        "role": "user",
        "content": f"My guess is: {guess}"
    })
    
    try:
        # 1) Call Gemini with tools
        response = client.chat.completions.create(
            model=MODEL,
            messages=game["messages"],
            tools=tools,
        )
        
        ai_message = response.choices[0].message
        
        # Track tool execution results
        game_was_ended = False
        feedback_raw = ""
        reason = None
        
        # Append assistant's thoughts/tool requests to chat history
        game["messages"].append({
            "role": "assistant",
            "content": ai_message.content or "",
            "tool_calls": ai_message.tool_calls,
        })
        
        # 2) If Gemini requested any tool execution, process them
        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                
                if name == "validate_word":
                    # Execute tool function
                    result = validate_word(args.get("guess", guess), game["secret_word"])
                    feedback_raw = result
                    
                    # Feed results back to Gemini
                    game["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    })
                    
                elif name == "end_game":
                    reason = args.get("reason", "LOST")
                    result = end_game(reason, args.get("answer", game["secret_word"]))
                    
                    # Feed results back to Gemini
                    game["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    })
                    game["game_over"] = True
                    game["reason"] = reason
                    game_was_ended = True
            
            # If we reached max guesses and the agent forgot to call end_game, enforce it
            if game["guesses_used"] >= MAX_GUESSES and not game["game_over"]:
                game["game_over"] = True
                game["reason"] = "LOST"
                
            # 3) Get follow-up narrative comment from Gemini
            follow_up = client.chat.completions.create(
                model=MODEL,
                messages=game["messages"],
            )
            
            reply = follow_up.choices[0].message.content
            game["messages"].append({
                "role": "assistant",
                "content": reply,
            })
            
        else:
            # If Gemini didn't make a tool call, fallback to manual evaluation
            reply = ai_message.content or "I've checked your guess."
            feedback_raw = validate_word(guess, game["secret_word"])
            
            if guess == game["secret_word"]:
                game["game_over"] = True
                game["reason"] = "WON"
            elif game["guesses_used"] >= MAX_GUESSES:
                game["game_over"] = True
                game["reason"] = "LOST"
                
        # Generate the beautiful feedback color list for the UI
        colors = get_feedback_colors(guess, game["secret_word"])
        
        # Cache results
        game["guesses"].append({
            "word": guess,
            "colors": colors
        })
        game["ai_messages"].append(reply)
        
        # Structure the API response
        response_data = {
            "status": "success",
            "guess": guess,
            "colors": colors,
            "feedback_raw": feedback_raw,
            "ai_message": reply,
            "guesses_used": game["guesses_used"],
            "max_guesses": MAX_GUESSES,
            "game_over": game["game_over"],
            "reason": game["reason"],
            "secret_word": game["secret_word"] if game["game_over"] else None
        }
        return jsonify(response_data)
        
    except Exception as e:
        print("Error in Gemini API / Agentic Loop:", e)
        return jsonify({"error": f"Failed to talk to Gemini API: {str(e)}"}), 500

if __name__ == "__main__":
    print("🤖 Starting AI Wordle Flask App...")
    print("👉 Open http://127.0.0.1:5000 in your browser to play!")
    app.run(debug=True, port=5000)
