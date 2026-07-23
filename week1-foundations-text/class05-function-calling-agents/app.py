"""
Wordle Saloon — Web App Backend 🤠🌵
====================================

This is the Flask backend server that powers our retro Wild West Wordle game.
It takes our command-line terminal agent from wordle_agent_starter.py and wraps
it in a web server so you can play it in the browser!

HOW IT WORKS (FOR BEGINNERS):
1. Flask is a lightweight Python web framework. It listens for requests from the
   browser (like "give me the home page" or "here is my guess") and returns responses
   (like HTML pages or JSON data).
2. Because HTTP is "stateless" (the server forgets who you are as soon as a request
   finishes), we use Flask's secure "session" cookies. It's like a safe locker on
   the user's browser where we store the secret word, how many guesses they used,
   and the running conversation history with the Gemini AI.
3. The "Agentic Loop" runs here! When you submit a guess:
   - We record your guess and append it to our ongoing chat history.
   - We call Gemini via its OpenAI-compatible SDK and supply it with a list of "tools".
   - Gemini decides whether it needs to check the word or end the game by making a
     "function call".
   - We run that function (e.g., validate_word) locally, append the result, and ask
     Gemini to make a friendly follow-up response in character as Sheriff Tex!
"""

import os
import json
import random
from flask import Flask, render_template, request, jsonify, session
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load the secret API key from the local .env file.
#    python-dotenv will read .env and set it in the OS environment variables.
load_dotenv()

# Ensure the key is present.
if not os.environ.get("GEMINI_API_KEY"):
    raise ValueError("⚠️ GEMINI_API_KEY not found in environment. Please check your .env file!")

# Initialize Flask
app = Flask(__name__)

# A secret key is required by Flask to sign the session cookies so users cannot temper with them.
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "wild-west-wordle-secret-1881-gold-rush")

# Configs
MODEL = "gemini-3.5-flash"
MAX_GUESSES = 6

# Initialize OpenAI client to interact with Gemini's OpenAI-compatible endpoint
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)


# ============================================================================
# WORDLE GAME LOGIC HELPERS
# ============================================================================

def get_secret_word():
    """Return one random 5-letter word from wordle.txt."""
    folder = os.path.dirname(__file__)  # folder where app.py lives
    path = os.path.join(folder, "wordle.txt")
    with open(path, "r") as file:
        words = [line.strip() for line in file if line.strip()]
    return random.choice(words).upper()


def validate_word(guess, secret_word):
    """Compare a 5-letter guess to the secret word and return emoji feedback."""
    guess = guess.strip().upper()
    secret_word = secret_word.strip().upper()

    if len(guess) != 5:
        return "That guess is not 5 letters. Ask the player to try again."

    feedback = []
    for i in range(5):
        if guess[i] == secret_word[i]:
            feedback.append("🟩")  # Correct letter, correct position
        elif guess[i] in secret_word:
            feedback.append("🟨")  # Letter is in the word, wrong position
        else:
            feedback.append("⬜")  # Letter is not in the word

    result = " ".join(feedback)
    if guess == secret_word:
        return f"{result} — CORRECT! The player guessed the word: {secret_word}"
    return f"Hint for '{guess}': {result}"


def end_game(reason, answer):
    """Return a friendly game-over message."""
    if reason == "WON":
        return f"🎉 You won! The word was {answer}. Nice guessing!"
    elif reason == "LOST":
        return f"😔 Out of guesses! The word was {answer}. Try again!"
    else:
        return f"👋 Game over ({reason}). The word was {answer}."


# ============================================================================
# GEMINI FUNCTION CALLING TOOL CONFIGURATIONS
# ============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "validate_word",
            "description": "Check the player's 5-letter guess against the secret word and return color feedback. Call this every time the player makes a guess.",
            "parameters": {
                "type": "object",
                "properties": {
                    "guess": {
                        "type": "string",
                        "description": "The player's 5-letter guess",
                    }
                },
                "required": ["guess"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "end_game",
            "description": "Call this when the game is over: the player won, ran out of guesses, or quit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "reason": {
                        "type": "string",
                        "description": "Why the game ended",
                        "enum": ["WON", "LOST", "QUIT"],
                    },
                    "answer": {
                        "type": "string",
                        "description": "The secret word",
                    },
                },
                "required": ["reason", "answer"],
            },
        },
    },
]


def serialize_message(message):
    """Convert an OpenAI/Gemini SDK message object into a simple serializable dict for Flask sessions."""
    serialized = {
        "role": message.role,
        "content": message.content or ""
    }
    if message.tool_calls:
        serialized["tool_calls"] = [
            {
                "id": tc.id,
                "type": tc.type,
                "function": {
                    "name": tc.function.name,
                    "arguments": tc.function.arguments
                }
            } for tc in message.tool_calls
        ]
    return serialized


# ============================================================================
# FLASK WEB ENDPOINTS (ROUTES)
# ============================================================================

@app.route("/")
def home():
    """Render the main Wordle Saloon page."""
    return render_template("index.html")


@app.route("/new_game", methods=["POST"])
def new_game():
    """Start a brand new game of Wordle. Resets session state."""
    secret_word = get_secret_word()

    # Reset all session states for this browser
    session["secret_word"] = secret_word
    session["guesses_used"] = 0
    session["game_over"] = False
    session["guesses"] = []  # Tracks guesses with letter statuses: [{'word': 'CRANE', 'letters': [{'letter': 'C', 'status': 'correct'}, ...]}]
    session["keyboard_status"] = {}  # Tracks letter states: {'C': 'correct', 'R': 'present'}
    session["game_reason"] = None

    # We craft an immersive, fun Wild West Game Master prompt
    system_prompt = (
        f"You are Sheriff Tex, a rugged, friendly but tough Wordle Game Master in a dusty frontier saloon in 1881. "
        f"The secret word is '{secret_word}' (always use UPPERCASE). "
        f"The player has {MAX_GUESSES} guesses. "
        f"Your job is to run the game of Wordle using function calling. "
        f"Follow these strict directives:\n"
        f"1. You MUST speak in a highly authentic, colorful, and thick Wild West cowboy dialect. "
        f"Use slang like 'Howdy', 'partner', 'y'all', 'reckon', 'varmint', 'yellow-bellied', 'belly up', 'shoot', 'gold nugget', etc. "
        f"Make it highly engaging, humorous, and brief. Keep text responses short (1-2 sentences).\n"
        f"2. Every single time the player types a 5-letter guess, you MUST immediately call the tool 'validate_word' with their guess. "
        f"Never try to validate the word yourself or guess colors without calling the tool.\n"
        f"3. When you receive the tool's result, comment on the result in character as Sheriff Tex (e.g. 'Ooh, a shiny gold nugget in the right spot!' or 'Dust and tumbleweeds, not a single matching letter!').\n"
        f"4. Keep track of how many guesses the player has used. If the player guesses the word correctly, call the 'end_game' tool with reason='WON'. "
        f"If they run out of guesses ({MAX_GUESSES} tries), call 'end_game' with reason='LOST'. "
        f"Never let them keep playing after the game is over.\n"
        f"5. Absolutely NEVER reveal the secret word '{secret_word}' in regular chat conversation. Only reveal it by calling 'end_game' or when the game has ended."
    )

    # Initialize chat history
    session["messages"] = [
        {"role": "system", "content": system_prompt}
    ]

    # Let's get an initial greeting from Sheriff Tex!
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=session["messages"]
        )
        greeting = response.choices[0].message.content or "Howdy partner! Step right up and let's see if you can guess my secret 5-letter word! You've got 6 bullet-tries. Draw!"
        session["messages"].append({"role": "assistant", "content": greeting})
    except Exception as e:
        greeting = f"Howdy partner! (Error reaching Gemini: {str(e)}). But let's play anyway!"
        session["messages"].append({"role": "assistant", "content": greeting})

    session.modified = True

    return jsonify({
        "status": "started",
        "greeting": greeting,
        "max_guesses": MAX_GUESSES
    })


@app.route("/guess", methods=["POST"])
def process_guess():
    """Handle a guess submitted by the user. Runs the agentic function calling loop."""
    if session.get("game_over"):
        return jsonify({"error": "The game has already ended! Saddle up and start a new one."}), 400

    # Read and clean the guess from incoming JSON request
    data = request.json or {}
    guess = data.get("guess", "").strip().upper()

    if len(guess) != 5 or not guess.isalpha():
        return jsonify({"error": "Whoa there, partner! A guess must be exactly 5 letters of the alphabet!"}), 400

    secret_word = session.get("secret_word")
    if not secret_word:
        return jsonify({"error": "No active game! Boot a new one."}), 400

    # 1. Update guess counts
    session["guesses_used"] = session.get("guesses_used", 0) + 1

    # 2. Append player's guess to messages
    session["messages"].append({"role": "user", "content": f"My guess is: {guess}"})

    reply = ""
    guess_feedback = None

    try:
        # 3. Call the model with our toolset
        response = client.chat.completions.create(
            model=MODEL,
            messages=session["messages"],
            tools=tools,
        )

        ai_message = response.choices[0].message
        # Add the AI's action/choice to session chat history
        session["messages"].append(serialize_message(ai_message))

        # 4. Process Tool Calls if Sheriff Tex decided to trigger them
        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if name == "validate_word":
                    # Execute validate_word local helper
                    guess_val = args.get("guess", guess).strip().upper()
                    result = validate_word(guess_val, secret_word)

                    # Store in message log
                    session["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    })

                    # Calculate color codes for our responsive frontend
                    feedback_statuses = ["absent"] * 5
                    secret_letters_tracking = list(secret_word)
                    guess_letters_tracking = list(guess_val)

                    # First pass: green boxes (correct spot)
                    for i in range(5):
                        if guess_letters_tracking[i] == secret_letters_tracking[i]:
                            feedback_statuses[i] = "correct"
                            secret_letters_tracking[i] = None
                            guess_letters_tracking[i] = None

                    # Second pass: yellow boxes (wrong spot)
                    for i in range(5):
                        if guess_letters_tracking[i] is not None:
                            if guess_letters_tracking[i] in secret_letters_tracking:
                                feedback_statuses[i] = "present"
                                # Consume first matching letter in tracking to avoid duplicate counts
                                match_idx = secret_letters_tracking.index(guess_letters_tracking[i])
                                secret_letters_tracking[match_idx] = None

                    # Format clean letter-by-letter structures for drawing tiles
                    guess_feedback = []
                    keyboard_status = session.get("keyboard_status", {})

                    for i in range(5):
                        letter = guess_val[i]
                        status = feedback_statuses[i]
                        guess_feedback.append({
                            "letter": letter,
                            "status": status
                        })

                        # Keyboard: 'correct' has highest priority, then 'present', then 'absent'
                        current_letter_status = keyboard_status.get(letter)
                        if current_letter_status != "correct":
                            if status == "correct" or (status == "present" and current_letter_status != "present"):
                                keyboard_status[letter] = status
                            elif current_letter_status is None:
                                keyboard_status[letter] = status

                    session["keyboard_status"] = keyboard_status

                    # Save full guesses history list
                    guesses = session.get("guesses", [])
                    guesses.append({
                        "word": guess_val,
                        "letters": guess_feedback
                    })
                    session["guesses"] = guesses

                elif name == "end_game":
                    # Execute end_game local helper
                    reason = args.get("reason", "LOST")
                    ans = args.get("answer", secret_word)
                    result = end_game(reason, ans)

                    # Store in message log
                    session["messages"].append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    })

                    session["game_over"] = True
                    session["game_reason"] = reason

            # After processing tool actions, run a second model pass (follow-up)
            # to formulate Tex's dialogue reacting to the tool feedback!
            follow_up = client.chat.completions.create(
                model=MODEL,
                messages=session["messages"]
            )
            reply = follow_up.choices[0].message.content or ""
            session["messages"].append({"role": "assistant", "content": reply})

        else:
            # If no tools were called (just general chat)
            reply = ai_message.content or "Shoot! I reckon something went slightly awry in my lassoing."
            session["messages"].append({"role": "assistant", "content": reply})

    except Exception as e:
        reply = f"Well, goldarnit! Something broke on the trail. Error: {str(e)}"
        session["messages"].append({"role": "assistant", "content": reply})

    # Save session back
    session.modified = True

    # If the user hit maximum guesses and the game master didn't automatically end it, end it here
    if session.get("guesses_used", 0) >= MAX_GUESSES and not session.get("game_over"):
        session["game_over"] = True
        session["game_reason"] = "LOST"
        reply += f" \n\n🤠 Tex says: '😔 Out of guesses, partner! The secret word was indeed {secret_word}. Dust yourself off and try again!'"
        session.modified = True

    return jsonify({
        "guess": guess,
        "feedback": guess_feedback,
        "guesses_used": session["guesses_used"],
        "max_guesses": MAX_GUESSES,
        "game_over": session["game_over"],
        "game_reason": session.get("game_reason"),
        "sheriff_reply": reply,
        "keyboard_status": session.get("keyboard_status", {}),
        "secret_word": secret_word if session["game_over"] else None
    })


# Start the Flask app local server
if __name__ == "__main__":
    # In development mode, we run on port 5000 with debug enabled
    # to restart the server on file changes.
    app.run(host="127.0.0.1", port=5000, debug=True)
