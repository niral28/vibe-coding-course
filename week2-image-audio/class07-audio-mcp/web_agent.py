
import requests
from pydantic import BaseModel, Field

import os
from dotenv import load_dotenv
import json
load_dotenv()

from google import genai
from openai import OpenAI

from stt_web_tts import generate_gemini_response, generate_loading_message, speech_to_text_gemini, record_audio_with_spacebar
from colorama import Fore, Back, Style

class Step(BaseModel):
    queries:list[str] = Field(description="The planned set of queries to take at this step")


class Plan(BaseModel):
    plan: list[Step]
    reasoning:str = Field(description="The thought process of how you're going to address the user's query")

class SearchResult(BaseModel):
    query: str
    summary: str = Field(description="The answer to the query, and if the answer is not found, extract+summarize any useful information in the text that could provide leads.")
    links: list[str] = Field(default_factory=list, description="List of the top 10 links found in the extracted text, should be in the format of https://en.wikipedia.org/wiki/...")




import uuid
def generate_call_id(prefix="call_"):
     return f"{prefix}{uuid.uuid4()}"


def web_search(query):
    from urllib.parse import quote
    quotedquery = quote(query)
    url = f"https://en.wikipedia.org/api/rest_v1/page/mobile-html/{quotedquery}"
    print(Fore.YELLOW + f'Fetching url: {url}....' + Style.DIM)
    print()
    response = requests.get(url)
    if response.status_code == 200:
        summary = response.text
        client = genai.Client()
        response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"You are responsible for extracting the answer from the wikipedia article. The query is: {quotedquery}. You must extract the answer from the wikipedia article, do not make up any information. If the answer is not found, return the answer as 'No answer found'. Also return the links to the wikipedia article or any related articles found in the extracted text. The wikipedia article is: {summary}",
        config={
            "response_mime_type": "application/json",
            "response_schema": SearchResult
        },
        )
        if response.text:
            print(Fore.CYAN + response.text+ Style.DIM)
        return response.text
    else:
        print(Fore.RED + f"Invalid search query. No articles found. Status code: {response.status_code}" + Style.DIM)
        return  f"No articles found for {query}. Status code: {response.status_code}. Try another or rephrase."

def web_open_link(link:str) -> str:
    client = genai.Client()
    response = requests.get(link)
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
        if response.text:
            print(Fore.CYAN + response.text+ Style.DIM)
        return response.text
    else:
        print(Fore.RED + f"Invalid link {link}. No articles found. Status code: {response.status_code}" + Style.DIM)
        return f"Invalid link {link}. No data found."


def chat_turns_to_string(messages:list[dict]):
    return "\n".join([f"{message['role']}: {message['content']}" for message in messages])

def generate_reflection(messages:list[dict]):
    client = genai.Client()
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

def generate_search_plan(query:str) -> str:
    client = genai.Client()
    response = client.models.generate_content(
        model="gemini-2.5-flash",
        contents=f"You're a deep research assistant. The user's question is: {query}. Please generate a search plan for the user's question, think step by step, break down the question into logicial steps and come up with a list of queries to search for the answer to the user's question. Do not make any assumptions, and do not rely on any your knowledge as it is outdated. Think from first principles.",
        config={
            "response_mime_type": "application/json",
            "response_schema": Plan
        },
        )
    if response.text:
        print(Fore.YELLOW + 'Search Plan: ' + Style.DIM, response.text)
        print()  
        return response.text
    else:
        return "Think step by step!"

from typing import Tuple
def execute_function(tool_name: str, args) -> Tuple[bool, str]:
    print(Fore.YELLOW + "Tool call: " + Style.DIM, tool_name, args)
    if tool_name == 'open_link':
        return (False, web_open_link(args.get('link', "")))
    elif tool_name == 'generate_search_plan':
        return (False, generate_search_plan(args.get('query', "")))
    elif tool_name == "encyclopedia_search":
        query = args.get("query")
        return (False, f"Query: {query}, Results: {web_search(query)}")
    elif tool_name == "answer_question":
        answer = args.get("answer", "")
        print(Fore.GREEN+"Breaking out of loop, answering question!")
        return (True, f"{answer}")
    else:
        return (False, "unknown function called!")
    


from datetime import datetime
def integrate_api_calls_with_gemini(model:str="gemini-2.5-flash", max_iterations:int=5, query:str=None, messages:list[dict]=None, query_style:str=None):
    count = 0
    google_client = genai.Client()
    model_info = google_client.models.get(model=model)
    print(f"{model_info.input_token_limit=}")
    print(f"{model_info.output_token_limit=}")

    client = OpenAI(
        api_key=os.environ['GEMINI_API_KEY'],
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    tools = [
        {
            "type": "function",
            "function": {
                "name": "generate_search_plan",
                "description": "Generate a search plan for the user's question, think step by step, break down the question into logicial steps and actions up with a list of queries to search for the answer to the user's question.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "The fully contextualized user question (e.g. for follow up questions, rephrase the question so all the information needed to answer the question is included)"}
                    },
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "encyclopedia_search",
                "description": "Search wikipedia directly for variety of facts and figures. Take a deep breath, break down the query and explain your thoughts before you call the tools.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {"type": "string", "description": "the name of the wikipedia article"}
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
        },
        {
            "type": "function",
            "function": {
                "name": "open_link",
                "description": "Fetch the data directly from a link. You may open multiple links to find the answer to the user's question. Typically you would open a link to follow a potential lead from a previous search.",
                "parameters": {
                    "type": "object",
                    "properties": { 
                        "link": {"type": "string", "description": "The url found in the extracted text should be in the format of https://en.wikipedia.org/wiki/..."},
                        "thought": {"type": "string", "description": "The reason for opening the link"}
                    },
                    "required": ["link", "thought"]
                }
            }
        }
    ]


    count=0
    answer_found = False
    while not answer_found:
        if count == max_iterations-1 or count == max_iterations:
            if count == max_iterations-2:
                turn ="second to last"
            else:
                turn = "last"
            messages.append({
                "role": "user", 
                "content":f"This is your {turn} chance to find the answer to the user's question. Please reflect on your previous attempts: {generate_reflection(list(messages))}"
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
            curr_tool_set = [tools[0]] if count==0 else tools
            tool_choice = 'required' if count==0 else 'auto'
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                tools=curr_tool_set,
                temperature=0.0,
                tool_choice=tool_choice
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
                tool_call.id = generate_call_id()
                args = json.loads(tool_call.function.arguments)
                if count%2==0 and query_style == "1":
                    print("Generating response for voice search")
                    if tool_call.function.name != 'answer_question':
                        generate_loading_message(query, tool_call.function.name)
                    else:
                        pass
                answer_found, content = execute_function(tool_call.function.name, args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_call.function.name,
                    "content": content
                })
                if answer_found:
                    break 
        if response.usage:
            print(f'Prompt Tokens:{response.usage.prompt_tokens}')
            input_token_limit = model_info.input_token_limit if model_info.input_token_limit else 0
            if input_token_limit > 0 and response.usage.prompt_tokens > 0 and input_token_limit/response.usage.prompt_tokens:
                print(f'Using {response.usage.prompt_tokens/input_token_limit}% of input tokens')
            if response.usage.prompt_tokens > 8000:
                print(f'Removing { messages.pop(1)}')
                print(f'Removing {messages.pop(1)}')
                
        count+=1

        print(Fore.BLUE + f"Count: {count}" + Style.DIM)
        print('-'*100)
        print('-'*100)
        if not answer_found:
            print(Fore.YELLOW + str(messages) + Style.DIM)
        print()
    print(Fore.GREEN+f'{content}')
    if query_style == '1':
           generate_gemini_response(f"Found it!....{content}")
    Style.RESET_ALL
    return messages

messages = [ {"role": "system", "content": f"You are a helpful research assistant. DO NOT rely on your own knowledge to answer any question, it is all outdated. You have access to a variety of tools to fetch information to answer the user's question.  Remember the information in the context may contain important information that you can use to answer follow up questions or come up with better search queries. Take a deep breath, before you call the tools break down the query and explain your thoughts, what are the keywords you are going to use to search the web. If the user asks you a question and the answer is not found try rephrasing the question and searching again. You may run parallel tool calls to search for the answer. Before you start searching a topic always generate a search plan. YOU GOT THIS!"},
    ]
    
user_quit = False
while not user_quit:
    query_style = input(Fore.BLUE + Style.BRIGHT + "What would you like to query today?, enter 1 for voice search, 2 for text search or 'exit' to quit\n" + Style.RESET_ALL)
    if query_style == "1":
        record_audio_with_spacebar()
        query = speech_to_text_gemini("input.wav")
    else:
        query = input(Fore.BLUE + Style.BRIGHT + "Enter your query: " + Style.RESET_ALL)
    if query == "exit":
        user_quit = True
        break
    messages.append({"role": "user", "content": f"[system] Today's date is: {datetime.now().strftime('%Y-%m-%d')}, the user's question is: {query}"})
    messages = integrate_api_calls_with_gemini(model="gemini-2.5-flash", query=query, messages=messages, query_style=query_style)
    query = ''
    query_style = ''