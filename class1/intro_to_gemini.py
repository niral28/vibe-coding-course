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
# generate_gemini_response("Tell me a good joke about vibe coders!", model="gemini-2.5-flash")

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
            {"role": "system", "content": "You are a Wordle game that the user plays via chat. Call get_user_input() when you need the user's guess. Call end_game() when the game is over (won, lost, or quit). You handle all game logic including tracking guesses, checking letters, and providing feedback."},
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

def validate_word(word):
    if not word or len(word.strip()) != 5:
        return False
    return True
    

# RAG with Gemini
# Extension ideas: Implement a get_hint_function, structured to show correct letters in the word, and incorrect letters in the word.
def chat_with_gemini_function_calling_with_rag(max_user_turns:int = 5, filename:str="worldle.txt", model:str="gemini-2.5-flash"):
    word_of_the_day = get_word_of_the_day(filename)
    print(f"Word of the day: {word_of_the_day}")

    messages = [
            {"role": "system", "content": f"You are a Wordle game that the user plays via chat. The word the user is trying to guess is: {word_of_the_day} . Call get_user_input() and validate_word() when you need the user's guess (parallel tool calls). Call end_game() when the game is over (won, lost) OR when the User quits. You handle all game logic including tracking guesses, checking letters, and providing feedback."},
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

                if response.choices[0].message.content:
                    print("Assistant: ", response.choices[0].message.content)
                print(tool_calls)

                queued_tool_calls = []
                for tool_call in tool_calls:
                    if tool_call.function.name == "validate_word":
                        print("CALLING validate_word")
                        queued_tool_calls.append(tool_call)
                        continue
                    
                    elif tool_call.function.name == "get_user_input":
                        print("CALLING get_user_input")
                        user_input = get_user_input()
                        queued_tool_calls.insert(0,tool_call)                        
                        continue
   
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

                user_input = None
                for tool_call in queued_tool_calls:
                    print(f"Tool call: {tool_call.function.name}")
                    if user_input is not None and tool_call.function.name == "validate_word":
                        print("CALLING validate_word")
                        res = validate_word(user_input)
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": "Validated" if res else "Invalid Input, ask user to try again, tell them the word must be 5 letters long"
                        })
                    elif tool_call.function.name == "get_user_input":
                        print("CALLING get_user_input")
                        user_input = get_user_input()
                        messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": f"User entered: {user_input}"
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


# chat_with_gemini_function_calling_with_rag(max_user_turns=3, filename="wordle.txt", model="gemini-2.5-flash")

# Interaractive Game -- exercise for you
import requests
def search_wikipedia(query):
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
        tools=tools,
        tool_choice="auto"
    )

    print(response.choices[0].message.content)
    # TODO: Design a quiz based on the information you found
    # Think about the game loop, how to make it more engaging and interactive

integrate_api_calls_with_gemini()