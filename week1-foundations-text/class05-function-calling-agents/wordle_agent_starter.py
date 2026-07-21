"""
GSET Vibe Coding — Class 5 Starter: AI Wordle Game Master 🟩🟨⬜
================================================================

WHAT YOU'RE BUILDING
  An AI that runs a game of Wordle *for you* in the terminal. You type 5-letter
  guesses; the AI uses TOOLS (functions you give it) to check each guess and it
  keeps the game going in a LOOP until you win or run out of guesses.

  Once this works in the terminal, you'll hand it to Antigravity and say
  "turn this into a web app" — see the README. Get the brain working first! 🧠
"""

# --- Libraries we use -------------------------------------------------------
import os
import json
import random
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gemini-3.5-flash"
MAX_GUESSES = 6

# ============================================================================
# Connect to Gemini
# ============================================================================
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# ============================================================================
# Pick a secret word
# ============================================================================
def get_secret_word():
    """Return one random 5-letter word from wordle.txt."""
    folder = os.path.dirname(__file__)
    path = os.path.join(folder, "wordle.txt")

    with open(path, "r") as file:
        words = [line.strip() for line in file if line.strip()]

    return random.choice(words).upper()

# ============================================================================
# Validate a guess
# ============================================================================
def validate_word(guess, secret_word):
    """Compare a 5-letter guess to the secret word and return emoji feedback."""
    guess = guess.strip().upper()
    secret_word = secret_word.strip().upper()

    if len(guess) != 5:
        return "That guess is not 5 letters. Ask the player to try again."

    feedback = []

    for i in range(5):
        if guess[i] == secret_word[i]:
            feedback.append("🟩")
        elif guess[i] in secret_word:
            feedback.append("🟨")
        else:
            feedback.append("⬜")

    result = " ".join(feedback)

    if guess == secret_word:
        return f"{result} — CORRECT! The player guessed the word: {secret_word}"

    return f"Hint for '{guess}': {result}"

# ============================================================================
# End game
# ============================================================================
def end_game(reason, answer):
    """Return a friendly game-over message."""
    if reason == "WON":
        return f"🎉 You won! The word was {answer}. Nice guessing!"
    elif reason == "LOST":
        return f"😔 Out of guesses! The word was {answer}. Try again!"
    else:
        return f"👋 Game over ({reason}). The word was {answer}."

# ============================================================================
# Tool Definitions
# ============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "validate_word",
            "description": (
                "Check the player's 5-letter guess against the secret word "
                "and return Wordle feedback using green, yellow, and gray "
                "squares. Call this tool every time the player makes a guess."
            ),
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
            "description": (
                "Call this when the game is over: the player won, "
                "ran out of guesses, or quit."
            ),
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

# ============================================================================
# Main Game Loop
# ============================================================================
def play_wordle():
    secret_word = get_secret_word()

    print("🟩 Welcome to AI Wordle! I'm thinking of a 5-letter word.")
    print(f"You have {MAX_GUESSES} guesses.\n")
    # print("psst... the word is", secret_word)

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

    messages = [
        {"role": "system", "content": system_prompt},
    ]

    game_over = False
    guesses_used = 0

    while not game_over and guesses_used < MAX_GUESSES:
        guess = input("Your guess: ").strip().upper()
        guesses_used += 1

        messages.append(
            {
                "role": "user",
                "content": f"My guess is: {guess}",
            }
        )

        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            tools=tools,
        )

        ai_message = response.choices[0].message

        messages.append(
            {
                "role": "assistant",
                "content": ai_message.content or "",
                "tool_calls": ai_message.tool_calls,
            }
        )

        if ai_message.tool_calls:
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                if name == "validate_word":
                    result = validate_word(args["guess"], secret_word)

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": name,
                            "content": result,
                        }
                    )

                elif name == "end_game":
                    result = end_game(args["reason"], args["answer"])

                    messages.append(
                        {
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": name,
                            "content": result,
                        }
                    )

                    game_over = True

            follow_up = client.chat.completions.create(
                model=MODEL,
                messages=messages,
            )

            reply = follow_up.choices[0].message.content

            messages.append(
                {
                    "role": "assistant",
                    "content": reply,
                }
            )

            print(f"\n🤖 {reply}\n")

        else:
            print(f"\n🤖 {ai_message.content}\n")

    print("Thanks for playing! 🎮")


if __name__ == "__main__":
    play_wordle()