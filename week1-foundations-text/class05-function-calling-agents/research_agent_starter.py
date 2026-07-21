"""
GSET Vibe Coding — Class 5 Starter: Wikipedia Research Agent 📚🔎
================================================================

WHAT YOU'RE BUILDING
  Ask a factual question and the AI answers it by *looking it up on Wikipedia*
  instead of guessing from memory. It searches, reads the article, and then
  answers WITH A SOURCE LINK — in a LOOP, until it has a grounded answer.

  This is called RAG (Retrieval-Augmented Generation): the AI "retrieves" real
  facts first, then writes its answer using them. RAG is one of the best ways to
  STOP an AI from "hallucinating" (making things up). See the README for more.

  Once this works in the terminal, hand it to Antigravity to make a web app.
"""

# --- Libraries we use -------------------------------------------------------
import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

MODEL = "gemini-3.5-flash"

# ============================================================================
# Connect to Gemini
# ============================================================================
client = OpenAI(
    api_key=os.environ["GEMINI_API_KEY"],
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

# ============================================================================
# Wikipedia Search Tool
# ============================================================================
def search_wikipedia(query):
    """Search Wikipedia and return {title, url, content} as text."""
    api = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "GSET-Vibe-Coding-Course/1.0 (classroom project)"}

    # Search for the best matching article
    search = requests.get(
        api,
        headers=headers,
        params={
            "action": "query",
            "list": "search",
            "srsearch": query,
            "format": "json",
            "srlimit": 1,
        },
    ).json()

    hits = search.get("query", {}).get("search", [])
    if not hits:
        return f"No Wikipedia article was found for '{query}'. Try different keywords."

    title = hits[0]["title"]

    # Get article summary
    summary = requests.get(
        api,
        headers=headers,
        params={
            "action": "query",
            "prop": "extracts",
            "exintro": True,
            "explaintext": True,
            "titles": title,
            "redirects": 1,
            "format": "json",
        },
    ).json()

    pages = summary.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    content = page.get("extract", "")[:2000]

    return json.dumps(
        {
            "title": title,
            "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
            "content": content,
        }
    )

# ============================================================================
# Function Calling Tools
# ============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": (
                "Search Wikipedia for facts about a topic and get a summary plus "
                "the source URL. Use this instead of guessing. You may call it "
                "multiple times."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords to search for.",
                    }
                },
                "required": ["query"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "give_answer",
            "description": (
                "Give the final answer using ONLY information obtained from "
                "Wikipedia, and include the Wikipedia URL used as the source."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The final answer using only Wikipedia.",
                    },
                    "source_url": {
                        "type": "string",
                        "description": "The Wikipedia URL used as the source.",
                    },
                },
                "required": ["answer", "source_url"],
            },
        },
    },
]

# ============================================================================
# Main Research Agent
# ============================================================================
def research():
    question = input("Ask a factual question: ").strip()

    system_prompt = (
        "You are a careful research assistant. "
        "Never answer from your own memory. "
        "Always use the search_wikipedia tool before answering. "
        "Answer ONLY using information returned by Wikipedia. "
        "If the search results are insufficient, search again using different keywords. "
        "If you still cannot find the answer, say so rather than making something up. "
        "When you are ready, call the give_answer tool with the final answer and "
        "the Wikipedia source URL."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    # Agentic loop
    for step in range(6):
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

        # If Gemini answered directly (without tool calls)
        if not ai_message.tool_calls:
            print(f"\n🤖 {ai_message.content}\n")
            return

        # Execute tool calls
        for tool_call in ai_message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name == "search_wikipedia":
                print(f"🔎 Searching Wikipedia for: {args['query']}")

                result = search_wikipedia(args["query"])

                messages.append(
                    {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": name,
                        "content": result,
                    }
                )

            elif name == "give_answer":
                print(f"\n🤖 {args['answer']}")
                print(f"📖 Source: {args['source_url']}\n")
                return

    print("Reached maximum number of search attempts.")

if __name__ == "__main__":
    research()