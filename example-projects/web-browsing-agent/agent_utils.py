import requests
from pydantic import BaseModel
import os
from dotenv import load_dotenv
import json
import uuid
from google import genai
from openai import OpenAI
from colorama import Fore, Back, Style
from datetime import datetime

load_dotenv()

class SearchResult(BaseModel):
    query: str
    answer: str
    success: bool
    links: list[str]

client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

def generate_call_id(prefix="call_"):
    return f"{prefix}{uuid.uuid4()}"

def search_wikipedia(query):
    from urllib.parse import quote
    query = quote(query)
    url = f"https://en.wikipedia.org/api/rest_v1/page/mobile-html/{query}"
    print(Fore.YELLOW + f'Fetching url: {url}....' + Style.DIM)
    print()
    response = requests.get(url)
    if response.status_code == 200:
        summary = response.text
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"You are responsible for extracting the answer from the wikipedia article. The query is: {query}. You must extract the answer from the wikipedia article, do not make up any information. If the answer is not found, return the answer as 'No answer found'. Also return the links to the wikipedia article or any related articles found in the extracted text. The wikipedia article is: {summary}",
        config={
            "response_mime_type": "application/json",
            "response_schema": SearchResult
        },
        )
        return response.text
    else:
        print(Fore.RED + f"Invalid search query. No articles found. Status code: {response.status_code}" + Style.DIM)
        return "Invalid search query. No articles found."

def chat_turns_to_string(messages: list[dict]):
    return "\n".join([f"{message['role']}: {message['content']}" for message in messages])

def generate_reflection(messages: list[dict]):
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"You're a deep research assistant but so far you have not been able to find the answer to the user's question. Please reflect on your previous attempts and try a different approach. Come up with several new approaches and return them in a list. Here's the conversation history:\n"+chat_turns_to_string(messages),
        config={
            "response_mime_type": "application/json",
            "response_schema": list[str]
        },
    )
    if response.text:
        print(Fore.YELLOW + 'Reflection: ' + Style.DIM, response.text)
        print()  
        return response.text
    else:
        return "Think step by step and come up with a new approach!"

def integrate_api_calls_with_gemini(model: str = "gemini-2.5-flash", max_iterations: int = 5, query: str = None, messages: list[dict] = None, query_style: str = None):
    count = 0
    client = OpenAI(
        api_key=os.environ['GEMINI_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    tools = [
        {
            "type": "function",
            "function": {
                "name": "encyclopedia_search",
                "description": "Search wikipedia for variety of facts and figures. Take a deep breath, break down the query and explain your thoughts before you call the tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "Keyword search query to find the relevant wikipedia article"}
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "answer_question",
                "description": "Answer the user's question based on the information you found. If the question is not answered successfully, try rephrasing the question and searching again.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "answer": {"type": "string", "description": "The answer to the user's question"},
                    },
                    "required": ["answer"]
                }
            }
        }
    ]

    count = 0
    answer_found = False
    while not answer_found:
        if count == max_iterations-1 or count == max_iterations:
            if count == max_iterations-2:
                turn = "second to last"
            else:
                turn = "last"
            messages.append({
                "role": "user", 
                "content": f"This is your {turn} chance to find the answer to the user's question. Please reflect on your previous attempts: {generate_reflection(list(messages))}"
            })
        
        if count > max_iterations:
            print("Reached max iterations, forcing answer")
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=[
                {
                "type": "function",
                "function": {
                    "name": "answer_question",
                    "description": "Answer the user's question based on the information you found. If the question is not answered successfully, and you have no more attempts, provide a summary of the information you found. If you have more attempts, try rephrasing the question and searching again.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "answer": {"type": "string", "description": "The answer to the user's question"},
                        },
                        "required": ["answer"]
                    }
                }
                },
                ],
                temperature=0.0,
                tool_choice="required"
            )
        else:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=tools,
                temperature=0.0,
                tool_choice="auto"
            )
            
        # Handle the response
        if response.choices[0].message.tool_calls:
            # Process tool calls
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                tool_call.id = generate_call_id()

            print(Fore.YELLOW + "Response: " + Style.DIM, response.choices[0].message)

            # Add the assistant's message with tool calls to history
            if response.choices[0].message.content and response.choices[0].message.tool_calls is None:
                print("Assistant: ", response.choices[0].message.content)
                messages.append({
                    "role": "assistant", 
                    "content": response.choices[0].message.content,
                })
            elif response.choices[0].message.content and tool_calls is not None:
                print("Assistant: ", response.choices[0].message.content)
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

        if response.choices[0].message.tool_calls:
            tool_calls = response.choices[0].message.tool_calls
            for tool_call in tool_calls:
                args = json.loads(tool_call.function.arguments)
                tool_call.id = generate_call_id()
                if tool_call.function.name == "encyclopedia_search":
                    query = args.get("query")
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": f"Encyclopedia search: {query}, Results: {search_wikipedia(query)}"
                    })
                elif tool_call.function.name == "answer_question":
                    answer = args.get("answer", "")
                    print(Fore.YELLOW + "Tool call: " + Style.DIM, tool_call)
                    print(Fore.YELLOW + "Args: " + Style.DIM, args)
                    messages.append({
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": tool_call.function.name,
                        "content": f"Encyclopedia answer: {answer}"
                    })
                    print(Fore.GREEN + "Breaking out of the loop" + Style.DIM)
                    print(Fore.BLUE + "Took ", count, "iterations to find the answer" + Style.DIM)
                    answer_found = True
                    break
        count += 1

        print(Fore.BLUE + f"Count: {count}" + Style.DIM)
        print('-'*100)
        if not answer_found:
            print(Fore.GREEN + str(messages) + Style.DIM)
        print()
    Style.RESET_ALL
    return messages