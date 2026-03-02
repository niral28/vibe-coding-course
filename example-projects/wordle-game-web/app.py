from flask import Flask, request, jsonify, render_template, send_from_directory
from flask_cors import CORS
import os
import sys
import uuid
import json
import random
from dotenv import load_dotenv
from openai import OpenAI

# Add the parent directory to the path so we can import from class1
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'class1'))

load_dotenv('../class1/.env')

app = Flask(__name__)
CORS(app, origins=['http://localhost:5001', 'http://127.0.0.1:5001', '*'])

# Global storage for active games (in production, use a proper database)
active_games = {}

class WordleGameSession:
    def __init__(self, game_id, word_of_the_day, model="gemini-2.5-flash"):
        self.game_id = game_id
        self.word_of_the_day = word_of_the_day
        self.model = model
        self.messages = [
            {"role": "system", "content": f"You are a Wordle game that the user plays via chat. The word the user is trying to guess is: {word_of_the_day}, they have 6 guesses! Call validate_word() when you receive a user's guess. Call end_game() when the game is over (won, lost, or after 6 guesses). You are responsible for driving the game loop. Each round the system will validate the guess and give them the hint (using color emojis, green 🟩 corresponds to letter in correct position, yellow 🟨 corresponds to letter in incorrect position, and gray ⬜ corresponds to letter not in the word) that you should display."},
            {"role": "user", "content": "[system] Start a new Wordle game"},
        ]
        self.curr_guess = ""
        self.hints_messages = []
        self.client = OpenAI(
            api_key=os.environ['GEMINI_API_KEY'],
            base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.game_over = False
        self.attempts = 0
        self.max_attempts = 6
        self.won = False
        
    def get_initial_message(self):
        """Get the initial AI response to start the game"""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.0
            )
            
            if response.choices[0].message.content:
                ai_message = response.choices[0].message.content
                self.messages.append({
                    "role": "assistant", 
                    "content": ai_message
                })
                return ai_message
            else:
                return "Welcome to Wordle! I'm thinking of a 5-letter word. You have 6 attempts to guess it!"
                
        except Exception as e:
            print(f"Error getting initial message: {e}")
            return "Welcome to Wordle! I'm thinking of a 5-letter word. You have 6 attempts to guess it!"
    
    def process_guess(self, guess):
        """Process a user's guess and return the AI response"""
        if self.game_over:
            return {
                "success": False,
                "error": "Game is already over",
                "game_over": True
            }
            
        if len(guess) != 5:
            return {
                "success": False,
                "error": "Guess must be exactly 5 letters"
            }
                
        try:
            # Add user's guess to messages
            self.messages.append({
                "role": "user",
                "content": f"My guess is: {guess.upper()}"
            })
            
            # Get AI response with function calling
            response = self.client.chat.completions.create(
                model=self.model,
                messages=self.messages,
                temperature=0.0,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "validate_word",
                            "description": "Validate the user's guess for the Wordle game and provide feedback",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "guess": {"type": "string", "description": "The user's 5-letter guess"}
                                },
                                "required": ["guess"]
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "end_game",
                            "description": "Call this function to end the game",
                            "parameters": {
                                "type": "object",
                                "properties": {
                                    "reason": {"type": "string", "description": "The reason for ending the game", "enum": ["WON", "LOST", "QUIT"]},
                                    "answer": {"type": "string", "description": "The correct answer"}
                                },
                                "required": ["reason", "answer"]
                            }
                        }
                    },
                ]
            )
            
            ai_message = ""
            feedback = None
            
            # Handle tool calls
            if response.choices[0].message.tool_calls:
                tool_calls = response.choices[0].message.tool_calls
                
                # Add assistant message with tool calls
                if response.choices[0].message.content:
                    ai_message = response.choices[0].message.content
                    
                self.messages.append({
                    "role": "assistant",
                    "content": response.choices[0].message.content or "",
                    "tool_calls": tool_calls
                })
                
                for tool_call in tool_calls:
                    tool_call.id = self.generate_call_id()
                    
                    if tool_call.function.name == "validate_word":
                        feedback = self.validate_word(guess, self.word_of_the_day)
                        # Only increment attempts for valid words (feedback is not None and not empty)
                        if feedback["feedback"] is not None and len(feedback["feedback"]) > 0:
                            self.attempts += 1
                            self.curr_guess = guess
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "validate_word",
                            "content": feedback["message"]
                        })
                        
                    elif tool_call.function.name == "end_game":
                        args = json.loads(tool_call.function.arguments)
                        reason = args.get("reason", "QUIT")
                        
                        if reason == "WON":
                            self.won = True
                        
                        self.game_over = True
                        
                        self.messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": "end_game", 
                            "content": f"Game ended: {reason}. Answer was: {self.word_of_the_day}"
                        })
                
                # Get final AI response after tool calls
                if not self.game_over or len([tc for tc in tool_calls if tc.function.name == "end_game"]) > 0:
                    final_response = self.client.chat.completions.create(
                        model=self.model,
                        messages=self.messages,
                        temperature=0.0
                    )
                    
                    if final_response.choices[0].message.content:
                        ai_message = final_response.choices[0].message.content
                        self.messages.append({
                            "role": "assistant",
                            "content": ai_message
                        })
            
            elif response.choices[0].message.content:
                ai_message = response.choices[0].message.content
                self.messages.append({
                    "role": "assistant",
                    "content": ai_message
                })
            
            # Check if game should end due to max attempts
            if self.attempts >= self.max_attempts and not self.game_over:
                self.game_over = True
                ai_message += f" Game Over! The word was: {self.word_of_the_day}"
            
            return {
                "success": True,
                "message": ai_message,
                "feedback": feedback["feedback"] if feedback else None,
                "game_over": self.game_over,
                "won": self.won,
                "answer": self.word_of_the_day if self.game_over else None,
                "attempts": self.attempts
            }
            
        except Exception as e:
            print(f"Error processing guess: {e}")
            return {
                "success": False,
                "error": f"Error processing guess: {str(e)}"
            }
    
    def validate_word(self, guess, correct_word):
        """Validate a guess and return feedback"""
        if not guess or len(guess.strip()) != 5:
            return {
                "message": "Invalid Input, word must be exactly 5 letters long",
                "feedback": None
            }

        guess = guess.strip().lower()
        correct_word = correct_word.strip().lower()
        if guess not in dictionary:
            return {
                "message": f"Invalid Input, word not in the dictionary!",
                "feedback": None
            }
        if guess == correct_word:
            return {
                "message": f"Correct! You guessed the word {correct_word}",
                "feedback": ["🟩", "🟩", "🟩", "🟩", "🟩"]
            }
        else:
            result = []
            for i in range(5):
                if guess[i] == correct_word[i]:
                    result.append("🟩")
                elif guess[i] in correct_word:
                    result.append("🟨")
                else:
                    result.append("⬜")
            
            return {
                "message": f'Hint: {" ".join(result)}',
                "feedback": result
            }
    
    def generate_call_id(self, prefix="call_"):
        return f"{prefix}{uuid.uuid4()}"

def get_word_of_the_day(filename="../class1/wordle.txt"):
    """Get a random word from the word list"""
    try:
        with open(filename, "r") as file:
            words = [line.strip() for line in file if line.strip()]
            word_of_the_day = random.choice(words).upper()
            print(f"Word of the day: {word_of_the_day}")
            return word_of_the_day
    except Exception as e:
        print(f"Error reading word file: {e}")
        # Fallback words if file can't be read
        fallback_words = ["ABOUT", "ABOVE", "ABUSE", "ACTOR", "ACUTE", "ADMIT", "ADOPT", "ADULT", "AFTER", "AGAIN"]
        return random.choice(fallback_words)

@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('.', 'index.html')

@app.route('/<path:filename>')
def serve_static(filename):
    """Serve static files"""
    # Add security headers and proper content types
    response = send_from_directory('.', filename)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    return response

@app.route('/api/new_game', methods=['POST'])
def new_game():
    print("New game requested")
    """Start a new Wordle game"""
    try:
        game_id = str(uuid.uuid4())
        word_of_the_day = get_word_of_the_day()
        
        # Create new game session
        game_session = WordleGameSession(game_id, word_of_the_day)
        active_games[game_id] = game_session
        
        # Get initial AI message
        initial_message = game_session.get_initial_message()
        
        return jsonify({
            "success": True,
            "game_id": game_id,
            "message": initial_message,
            "word": word_of_the_day  # Remove this in production!
        })
        
    except Exception as e:
        print(f"Error creating new game: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/submit_guess', methods=['POST'])
def submit_guess():
    """Submit a guess for the Wordle game"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        guess = data.get('guess', '').upper()
        
        if not game_id or game_id not in active_games:
            return jsonify({
                "success": False,
                "error": "Invalid game ID"
            }), 400
            
        game_session = active_games[game_id]
        result = game_session.process_guess(guess)
        
        # Clean up completed games
        if result.get("game_over"):
            # Keep the game for a bit in case user wants to see final state
            pass
            
        return jsonify(result)
        
    except Exception as e:
        print(f"Error submitting guess: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500


@app.route('/api/get_hint', methods=['POST'])
def get_hint():
    """Get a hint for the current game using Gemini AI"""
    try:
        data = request.get_json()
        game_id = data.get('game_id')
        
        if not game_id or game_id not in active_games:
            return jsonify({
                "success": False,
                "error": "Invalid game ID"
            }), 400
            
        game_session = active_games[game_id]
        
        if game_session.game_over:
            return jsonify({
                "success": False,
                "error": "Game is already over"
            })
        
        word = game_session.word_of_the_day
        attempts = game_session.attempts
        
        # Initialize hints_messages if not already done
        if not hasattr(game_session, 'hints_messages') or not game_session.hints_messages:
            game_session.hints_messages = [{
                "role": "system",
                "content": f"You are a helpful assistant that gives hints for Wordle games. The target word is '{word}'. The user's current guess is '{game_session.curr_guess}'. Give creative, helpful hints without revealing the word directly. Vary your hint style - you can mention letter count, provide riddles that give hints about the word and its meaning, word characteristics, rhymes, definitions. Or provide several candidiate words based on how many attempts the user has made. Don't repeat previous hints."
            }]
        
        # Create the hint request message
        hint_request = f"Give me a helpful hint for the Wordle game. The word is '{word}' (5 letters). The user has made {attempts} attempts so far. Please provide a creative, helpful hint without revealing the word directly. Make it progressively more helpful if they've made more attempts."
        
        # Add the current hint request
        game_session.hints_messages.append({
            "role": "user", 
            "content": hint_request
        })
        
        # Get AI-generated hint
        response = game_session.client.chat.completions.create(
            model=game_session.model,
            messages=game_session.hints_messages,
            temperature=0.7  # Higher temperature for more creative hints
        )
        
        hint_text = response.choices[0].message.content
        
        # Add AI response to hints history
        game_session.hints_messages.append({
            "role": "assistant",
            "content": hint_text
        })
        
        return jsonify({
            "success": True,
            "hint": f"💡 {hint_text}"
        })
        
    except Exception as e:
        print(f"Error getting hint: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

@app.route('/api/game_status/<game_id>', methods=['GET'])
def game_status(game_id):
    """Get the current status of a game"""
    try:
        if game_id not in active_games:
            return jsonify({
                "success": False,
                "error": "Game not found"
            }), 404
            
        game_session = active_games[game_id]
        
        return jsonify({
            "success": True,
            "game_over": game_session.game_over,
            "attempts": game_session.attempts,
            "max_attempts": game_session.max_attempts,
            "won": game_session.won
        })
        
    except Exception as e:
        print(f"Error getting game status: {e}")
        return jsonify({
            "success": False,
            "error": str(e)
        }), 500

dictionary = []
if __name__ == '__main__':
    print("Starting Wordle Web Server...")
    print("Make sure you have GEMINI_API_KEY set in class1/.env")
    print("Visit http://localhost:5001 to play!")
    filename = "../class1/wordle.txt"
    with open(filename, "r") as file:
        dictionary = [line.strip() for line in file if line.strip()]
    print(f"Total words: {len(dictionary)}")
    print(f"First 10 words: {dictionary[:10]}")
    print(f"Last 10 words: {dictionary[-10:]}")
    app.run(debug=True, port=5001)