# Let's create your first AI-powered program!

import os
from dotenv import load_dotenv
load_dotenv()


## Hello World with Gemini 🌟
# https://ai.google.dev/gemini-api/docs/quickstart 

from google import genai
# The client gets the API key from the environment variable `GEMINI_API_KEY`.
def generate_gemini_response(prompt:str, model:str="gemini-2.5-flash"):
    client = genai.Client()

    response = client.models.generate_content(
        model=model, contents=prompt
    )
    print(response.text, model)


# Feel free to change the prompt and model to see how the response changes!
# Models listed at: https://ai.google.dev/gemini-api/docs/models
# generate_gemini_response("Who's the president of the United States?", model="gemini-2.5-flash")

# Ok now that we've got the basics down, let's start building some more complex programs!

from openai import OpenAI
# An interactive chatbot!
def chat_with_gemini(max_user_turns:int = 5, model:str="gemini-2.5-flash"):

    # Initialize the messages list with the system prompt
    messages=[
            {"role": "system", "content": "You are a worlde game that the user plays via chat"},
            {"role": "user", "content": "Start the game, (note the clock has started)"},
        ]
    count=0
    client = OpenAI(
        api_key=os.environ['GEMINI_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    print("Let's chat with Gemini!")
    print(messages)
    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0 # 0.0 is the most deterministic response, 1.0 is the most random
    )
    print(f'Assistant: {response.choices[0].message.content}')

    while count < max_user_turns:
        request = input('User: ')
        if request.strip() == 'q':
            print('Exiting!')
            break
        while True:
            if request:
                messages.append({'role': 'user', 'content': request})
                break
            else:
                print('Please provide a valid message (cannot be empty)')
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        count+=1
        if response.choices[0] and response.choices[0].message.content:
            messages.append(
                {"role": "assistant", "content": response.choices[0].message.content}
            )
            print(f'Assistant: {response.choices[0].message.content}')
    if count == max_user_turns:
        print("(system)Reached Chat Limit, Tell the user the answer!")
        messages.append(
            {"role": "user", "content": "[system] Times up! Let the user know they lost and tell them the answer!"}
        )
        response = client.chat.completions.create(
            model=model,
            messages=messages
        )
        print(f'Assistant: {response.choices[0].message.content}')
    print(messages)
# chat_with_gemini(max_user_turns=2, model="gemini-2.5-flash")



# Now let's start making it more complex, let's integrate function calling!
# https://ai.google.dev/gemini-api/docs/function-calling

def get_user_input():
    while True:
        request = input('User: ')
        if request:
            return request
        else:
            print('Please provide a valid message (cannot be empty)')

# An interactive chatbot!

# This is a simple Wordle game that the user plays via chat.
# Extension ideas: Implement a get_hint_function, get_word_of_the_day_function, validate_word_function, etc.
def chat_with_gemini_function_calling(max_user_turns:int = 5, model:str="gemini-2.5-pro"):
    messages = [
            {"role": "system", "content": "You are a Wordle game that the user plays via chat. Call get_user_input() when you need the user's guess. Note the user may quit the game by typing in 'q'. You handle all game logic including tracking guesses, checking letters, and providing feedback. Each round the system will validate the guess and give them the hint (using color emojis, green corresponds to letter in correct position, yellow corresponds to letter in incorrect position, and gray corresponds to letter not in the word) that you should display."},
            {"role": "user", "content": "[system] Start a new Wordle game"},
        ]
    
    count = 0
    client = OpenAI(
        api_key=os.environ['GEMINI_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    game_over = False
    
    while not game_over and count < 20:  # Increased max iterations
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_user_input",
                            "description": "Get the user's guess for the Wordle game",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
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
                                    "reason": {"type": "string", "description": "The reason for ending the game"},
                                    "answer": {"type": "string", "description": "The correct answer"}
                                },
                                "required": ["reason", "answer"]
                            }
                        }
                    },
                ],
                # Remove tool_choice="required" to allow normal responses
            )
            
            count += 1
            print(f"Count: {count}")
            
            # Handle the response
            if response.choices[0].message.tool_calls:
                # Process tool calls
                tool_calls = response.choices[0].message.tool_calls
                
                # Add the assistant's message with tool calls to history
                if response.choices[0].message.content:
                    messages.append({
                        "role": "assistant", 
                        "content": response.choices[0].message.content,
                        "tool_calls": tool_calls
                    })

                if response.choices[0].message.content and response.choices[0].message.content.strip() != "":
                    print("Assistant: ", response.choices[0].message.content)
    
                for tool_call in tool_calls:
                    if tool_call.function.name == "get_user_input":
                        print("CALLING get_user_input")

                        user_input = get_user_input()
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": user_input
                        })
                        
                    elif tool_call.function.name == "end_game":
                        print("CALLING end_game")
                        import json
                        args = json.loads(tool_call.function.arguments)
                        reason = args.get("reason", "Game ended")
                        answer = args.get("answer", "Unknown")
                        
                        print(f"Game Over! Reason: {reason}, Answer: {answer}")
                        game_over = True
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"Game ended: {reason}. Answer was: {answer}"
                        })
                        
            elif response.choices[0].message.content:
                # Regular response without tool calls
                content = response.choices[0].message.content
                print(f'Assistant: {content}')
                
                # Add assistant's message to history
                messages.append({
                    "role": "assistant", 
                    "content": content
                })
                
            else:
                print("No content or tool calls received")
                break
                
        except Exception as e:
            print(f"Error: {e}")
            break
    
    print("Game session ended")

# chat_with_gemini_function_calling(max_user_turns=3, model="gemini-2.5-flash")

import random
def get_word_of_the_day(filename):
    # Reservoir sampling to pick a random line without loading the whole file
    result = None
    with open(filename, "r") as file:
        for i, line in enumerate(file, 1):
            if random.randrange(i) == 0:
                result = line.strip()
    return result

def validate_word(guess:str, correct_word:str) -> str:
    if not guess or len(guess.strip()) != 5:
        return "Invalid Input, ask user to try again, tell them the word must be exactly 5 letters long"

    if guess.strip().lower() == correct_word.strip().lower():
        return f"User correctly guessed the word {correct_word}"
    else:
        result = []
        for i in range(5):
            if guess[i].lower() == correct_word[i].lower():
                result.append("🟩")
            elif guess[i].lower() in correct_word.lower():
                result.append("🟨")
            else:
                result.append("⬜")
    return f'This is the next hint(based on the correct position of the letters): {" | ".join(result)}'
    

def end_game(reason:str, answer:str) -> str:
    if reason == 'WON':
        return f"Congratulations, you won the game!! 🎉🎉🎉"
    elif reason == 'LOST':
        return f"Sorry! You lost the game. 😔 Correct answer was: {answer}"
    else:
        return f"Game ended: {reason}. I'm sorry you quit. 🫠 Correct answer was: {answer}"

import uuid
def generate_call_id(prefix="call_"):
     return f"{prefix}{uuid.uuid4()}"

# RAG with Gemini
# Extension ideas: Implement a get_hint_function, structured to show correct letters in the word, and incorrect letters in the word.
def chat_with_gemini_function_calling_with_rag(max_user_turns:int = 5, filename:str="wordle.txt", model:str="gemini-2.5-flash"):
    word_of_the_day = get_word_of_the_day(filename)
    print(f"Word of the day: {word_of_the_day}")

    messages = [
            {"role": "system", "content": f"You are a Wordle game that the user plays via chat. The word the user is trying to guess is: {word_of_the_day}, they have 5 guesses! . Call get_user_input() and validate_word() when you need the user's guess (parallel tool calls). Call end_game() when the game is over (won, lost) OR when the User quits."+ \
            "You are responsible for driving the game loop. Each round the system will validate the guess and give them the hint (using color emojis, green 🟩 corresponds to letter in correct position, yellow 🟨 corresponds to letter in incorrect position, and gray ⬜ corresponds to letter not in the word) that you should display."},
            {"role": "user", "content": "[system] Start a new Wordle game"},
        ]
    
    count = 0
    client = OpenAI(
        api_key=os.environ['GEMINI_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    
    game_over = False
    
    while not game_over and count < 20:  # Increased max iterations
        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0.0,
                tools=[
                    {
                        "type": "function",
                        "function": {
                            "name": "get_user_input",
                            "description": "Get the user's guess for the Wordle game",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
                            }
                        }
                    },
                    {
                        "type": "function",
                        "function": {
                            "name": "validate_word",
                            "description": "Validate the user's guess for the Wordle game. Always call this function after calling get_user_input()",
                            "parameters": {
                                "type": "object",
                                "properties": {},
                                "required": []
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
                                    "reason": {"type": "enum", "description": "The reason for ending the game", "enum": ["WON", "LOST", "QUIT"]},
                                    "answer": {"type": "string", "description": "The correct answer"}
                                },
                                "required": ["reason", "answer"]
                            }
                        }
                    },
                ],
                # Remove tool_choice="required" to allow normal responses
            )
            
            count += 1
            print(f"Count: {count}")
            guess_count=0
            # Handle the response
            if response.choices[0].message.tool_calls:
                # Process tool calls
                tool_calls = response.choices[0].message.tool_calls
                for tool_call in tool_calls:
                    tool_call.id = generate_call_id()

                print(response.choices[0].message)

                # Add the assistant's message with tool calls to history
                if response.choices[0].message.content and response.choices[0].message.tool_calls is None:
                    messages.append({
                        "role": "assistant", 
                        "content": response.choices[0].message.content,
                    })
                elif response.choices[0].message.content and tool_calls is not None:
                    messages.append({
                        "role": "assistant", 
                        "content": response.choices[0].message.content,
                        "tool_calls": tool_calls
                    })
                elif tool_calls:
                    messages.append({
                        "role": "assistant", 
                        "content": "",
                        "tool_calls": tool_calls
                    })
                else:
                    messages.append({
                        "role": "assistant", 
                        "content": "No response from the assistant, try again"
                    })

                if response.choices[0].message.content:
                    print("Assistant: ", response.choices[0].message.content)
                print()
                print(messages)
                print()

                user_input = None
                
                for tool_call in tool_calls:
                    if tool_call.function.name == "get_user_input":
                        print("CALLING get_user_input")
                        user_input = get_user_input()
                        guess_count+=1
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "name": tool_call.function.name,
                            "content": f"User entered: {user_input} [This was guess {guess_count}/5]"
                        })
                        
                    elif tool_call.function.name == "validate_word":
                        print("CALLING validate_word")
                        if user_input is not None:
                            res = validate_word(user_input, word_of_the_day)
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name":  tool_call.function.name,
                                "content": res
                            })
                        else:
                            messages.append({
                                "role": "tool",
                                "tool_call_id": tool_call.id,
                                "name": tool_call.function.name,
                                "content": "Error: No user input to validate"
                            })
                            
                    elif tool_call.function.name == "end_game":
                        print("CALLING end_game")
                        import json
                        args = json.loads(tool_call.function.arguments)
                        reason = args.get("reason", "Game ended")
                        if reason not in ["WON", "LOST", "QUIT"]:
                            reason = "QUIT"

                        print(f"Game Over! Reason: {reason}, Answer: {answer}")
                        game_over = True
                        
                        # Add tool result to messages
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": end_game()
                        })
            elif response.choices[0].message.content:
                # Regular response without tool calls
                content = response.choices[0].message.content
                print(f'Assistant: {content}')
                
                # Add assistant's message to history
                messages.append({
                    "role": "assistant", 
                    "content": content
                })
                
            else:
                print("No content or tool calls received")
                break
                
        except Exception as e:
            print(messages)
            print(f"Error: {e}")
            break
    
    print("Game session ended")


chat_with_gemini_function_calling_with_rag(max_user_turns=3, filename="wordle.txt", model="gemini-2.5-pro")

# Interaractive Game -- exercise for you
import requests
def search_wikipedia(query):
    from urllib.parse import quote
    query = quote(query)
    url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{query}"
    response = requests.get(url)
    return response.json()


from datetime import datetime
def integrate_api_calls_with_gemini(model:str="gemini-2.5-flash"):
    messages = [
            {"role": "system", "content": f"You are a helpful assistant that can search wikipedia for variety of facts and figures. And responsible for designing quizzes based on the information you find."},
            {"role": "user", "content": f"[system] Find the information about something that happened in history today: {datetime.now().strftime('%Y-%m-%d')}"},
        ]
    
    count = 0
    client = OpenAI(
        api_key=os.environ['GEMINI_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )

    tools = [
        {
            "type": "function",
            "name": "encyclopedia_search",
            "description": "Search wikipedia for variety of facts and figures.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Keyword search query to find the relevant wikipedia article"}
                },
                "required": ["query"]
            }
        }
    ]

    response = client.chat.completions.create(
        model=model,
        messages=messages,
        temperature=0.0,
        tool_choice="auto"
    )

    print(response.choices[0].message.content)
    # TODO: Design a quiz based on the information you found
    # Think about the game loop, how to make it more engaging and interactive

# integrate_api_calls_with_gemini(model="gemini-2.5-pro")