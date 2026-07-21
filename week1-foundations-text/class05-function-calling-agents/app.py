import os
import json
import requests
from dotenv import load_dotenv
from openai import OpenAI
from flask import Flask, request, jsonify, render_template
from flask_cors import CORS

# Load .env file from the current directory
load_dotenv()

MODEL = "gemini-3.5-flash"

# Validate API key
api_key = os.environ.get("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not found in environment. Please add it to your .env file.")

# Initialize the OpenAI-compatible client for Gemini
client = OpenAI(
    api_key=api_key,
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
)

app = Flask(__name__)
CORS(app)  # Enable Cross-Origin Resource Sharing

# ============================================================================
# Wikipedia Search Tool
# ============================================================================
def search_wikipedia(query):
    """Search Wikipedia and return {title, url, content} as a dictionary/string."""
    api = "https://en.wikipedia.org/w/api.php"
    headers = {"User-Agent": "GSET-Vibe-Coding-Course/1.0 (classroom project)"}

    # 1) Find the best-matching article title
    try:
        response = requests.get(api, headers=headers, params={
            "action": "query", "list": "search", "srsearch": query,
            "format": "json", "srlimit": 1,
        }, timeout=10)
        search = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return f"Wikipedia search failed ({e}). Try again or use different keywords."
    
    hits = search.get("query", {}).get("search", [])
    if not hits:
        return f"No Wikipedia article was found for '{query}'. Try different keywords."

    title = hits[0]["title"]

    # 2) Get a clean, plain-text summary (the article's intro)
    try:
        response = requests.get(api, headers=headers, params={
            "action": "query", "prop": "extracts", "exintro": True,
            "explaintext": True, "titles": title, "redirects": 1, "format": "json",
        }, timeout=10)
        summary = response.json()
    except (requests.exceptions.RequestException, ValueError) as e:
        return f"Wikipedia lookup for '{title}' failed ({e}). Try again or use different keywords."
    
    pages = summary.get("query", {}).get("pages", {})
    page = next(iter(pages.values()), {})
    content = page.get("extract", "")[:2000]  # Keep it reasonably short

    return json.dumps({
        "title": title,
        "url": f"https://en.wikipedia.org/wiki/{title.replace(' ', '_')}",
        "content": content,
    })


# ============================================================================
# Function Calling Tool Definitions
# ============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "search_wikipedia",
            "description": "Search Wikipedia for facts about a topic and get a "
                           "summary plus the source URL. Use this to look things "
                           "up instead of guessing. You can call it more than once.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Keywords to search for, e.g. 'tallest mountain'",
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
            "description": "Give the final answer to the user based only on the Wikipedia results, "
                           "and include the source URL you used.",
            "parameters": {
                "type": "object",
                "properties": {
                    "answer": {
                        "type": "string",
                        "description": "The final answer, using only what you found",
                    },
                    "source_url": {
                        "type": "string",
                        "description": "The Wikipedia URL the answer came from",
                    },
                },
                "required": ["answer", "source_url"],
            },
        },
    },
]


# ============================================================================
# Core Agentic RAG Loop
# ============================================================================
def run_research_agent(question):
    # The anti-hallucination system prompt that anchors the agent
    system_prompt = (
        "You are a careful and helpful research assistant.\n"
        "You must NOT use your own memory — facts may be outdated or wrong.\n"
        "You must call search_wikipedia to find facts FIRST.\n"
        "You must answer ONLY using what the search returned.\n"
        "If the search doesn't contain the answer, search again with different keywords, "
        "or say you couldn't find it (never make it up).\n"
        "When ready, call give_answer with the answer AND the source URL."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": question},
    ]

    steps = []

    # Maximum 6 iterations for safety and preventing infinite loops
    for step_idx in range(6):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=messages,
                tools=tools,
            )
        except Exception as e:
            return {
                "success": False,
                "error": f"Gemini API request failed: {str(e)}",
                "steps": steps
            }

        ai_message = response.choices[0].message
        content_text = ai_message.content or ""

        # Save model thoughts if it output text before calling tools
        if content_text.strip():
            steps.append({
                "type": "thought",
                "content": content_text
            })

        # Append assistant response to conversational state
        messages.append({
            "role": "assistant",
            "content": content_text,
            "tool_calls": ai_message.tool_calls,
        })

        # Case 1: The AI didn't request any tools (direct response)
        if not ai_message.tool_calls:
            return {
                "success": True,
                "answer": content_text,
                "source_url": None,
                "steps": steps
            }

        # Case 2: Process the tool requests
        for tool_call in ai_message.tool_calls:
            name = tool_call.function.name
            args = json.loads(tool_call.function.arguments)

            if name == "search_wikipedia":
                query = args.get("query", "")
                steps.append({
                    "type": "search_wikipedia",
                    "query": query,
                    "summary": f"Searching Wikipedia for: '{query}'"
                })

                result_json = search_wikipedia(query)
                
                # Try to parse content summary for cleaner logging
                try:
                    parsed_res = json.loads(result_json)
                    result_summary = parsed_res.get("content", "")[:200] + "..."
                except Exception:
                    result_summary = result_json[:200]

                # Append tool result to history so the model can read it
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result_json,
                })

                # Record the retrieval result
                steps.append({
                    "type": "search_result",
                    "query": query,
                    "summary": f"Wikipedia returned content snippet.",
                    "detail": result_summary
                })

            elif name == "give_answer":
                answer = args.get("answer", "")
                source_url = args.get("source_url", "")

                steps.append({
                    "type": "give_answer",
                    "answer": answer,
                    "source_url": source_url,
                    "summary": "Delivered grounded answer based on source link."
                })

                return {
                    "success": True,
                    "answer": answer,
                    "source_url": source_url,
                    "steps": steps
                }

    # If loop concludes without give_answer call
    return {
        "success": False,
        "error": "The agent was unable to find or formulate a grounded answer within 6 steps.",
        "steps": steps
    }


# ============================================================================
# Flask Router Configuration
# ============================================================================
@app.route("/")
def home():
    """Render the main front-end application."""
    return render_template("index.html")


@app.route("/api/research", methods=["POST"])
def api_research():
    """Run research agent and return structured JSON logs & result."""
    data = request.get_json() or {}
    question = data.get("question", "").strip()

    if not question:
        return jsonify({"success": False, "error": "Question is required."}), 400

    result = run_research_agent(question)
    return jsonify(result)


if __name__ == "__main__":
    # Use port 5001 to prevent collisions with AirPlay on macOS Monterey+ (which takes port 5000)
    print("🚀 Wikipedia Research Agent Server starting on http://127.0.0.1:5001...")
    app.run(host="127.0.0.1", port=5001, debug=True)
