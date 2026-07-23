"""
GSET Vibe Coding — Class 5, Option D: Bill-Splitting Agent 🧾💸
================================================================

WHAT YOU'RE BUILDING
  Tell the AI about expenses as you go ("add $20 for pizza", "add $15 for
  drinks"), then ask it to split the bill ("split between 4 people, 15%
  tip") and it works out exactly how much each person owes.

TWO BIG IDEAS
  • FUNCTION CALLING  -> the AI calls Python tools instead of doing math itself.
  • AGENTIC LOOP      -> you can add several expenses in a row, then ask for
                         the split, all in one running conversation — the AI
                         takes as many steps as it needs without you editing
                         any code in between.

HOW TO RUN IT
  1. Make sure .env in this folder has your GEMINI_API_KEY.
  2. From the project's ROOT folder, with (gset-vibes) active:

       python week1-foundations-text/class05-function-calling-agents/bill_splitting_agent.py

  3. Try it out:
       add $20 for pizza
       add $15 for drinks
       we're in Japan — split between 4 people
       done
------------------------------------------------------------------------------
"""

import os
import json
from dotenv import load_dotenv     # reads your GEMINI_API_KEY from the .env file
from openai import OpenAI          # we talk to Gemini through its OpenAI-compatible endpoint

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
# Session state — the running list of expenses for this conversation
# ============================================================================
expenses = []


# ============================================================================
# Tool #1: add an expense to the running tab
# ============================================================================
def add_expense(description, amount):
    """Add an expense to the tab and return the new running total."""
    expenses.append({"description": description, "amount": amount})
    total = sum(item["amount"] for item in expenses)
    return json.dumps({
        "added": {"description": description, "amount": amount},
        "running_total": round(total, 2),
        "expense_count": len(expenses),
    })


# ============================================================================
# Tool #2: split the running total (plus tax and tip) evenly between people
# ============================================================================
def calculate_split(num_people, tip_percent=0, tax_percent=0):
    """Add tax + tip to the running total and divide evenly among num_people."""
    subtotal = sum(item["amount"] for item in expenses)
    tax = subtotal * (tax_percent / 100)
    tip = subtotal * (tip_percent / 100)
    total = subtotal + tax + tip
    per_person = total / num_people if num_people else 0
    return json.dumps({
        "subtotal": round(subtotal, 2),
        "tax_percent": tax_percent,
        "tax_amount": round(tax, 2),
        "tip_percent": tip_percent,
        "tip_amount": round(tip, 2),
        "total": round(total, 2),
        "num_people": num_people,
        "amount_per_person": round(per_person, 2),
    })


# ============================================================================
# The menu of tools we give the AI (function calling)
# ============================================================================
tools = [
    {
        "type": "function",
        "function": {
            "name": "add_expense",
            "description": "Add one expense to the running tab. Call this once "
                           "for each item/expense the user mentions.",
            "parameters": {
                "type": "object",
                "properties": {
                    "description": {
                        "type": "string",
                        "description": "What the expense was for, e.g. 'pizza'",
                    },
                    "amount": {
                        "type": "number",
                        "description": "The dollar amount of the expense",
                    },
                },
                "required": ["description", "amount"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "calculate_split",
            "description": "Add tax and tip to the running total and split the whole "
                           "bill evenly among a number of people. Call this only "
                           "after all expenses have been added, once the user "
                           "asks to split the bill.",
            "parameters": {
                "type": "object",
                "properties": {
                    "num_people": {
                        "type": "integer",
                        "description": "How many people are splitting the bill",
                    },
                    "tip_percent": {
                        "type": "number",
                        "description": "Tip as a percent, e.g. 15 for 15%. "
                                       "Use 0 if the user doesn't mention a tip.",
                    },
                    "tax_percent": {
                        "type": "number",
                        "description": "Sales tax or VAT as a percent, e.g. 8.875 for New York. "
                                       "If the user mentioned what country they're in, use your "
                                       "knowledge of that country's typical rate. Use 0 otherwise.",
                    },
                },
                "required": ["num_people"],
            },
        },
    },
]


# ============================================================================
# The agent's instructions (shared by the terminal and web versions)
# ============================================================================
SYSTEM_PROMPT = (
    "You are a friendly bill-splitting assistant. As the user mentions "
    "expenses, call add_expense once per expense to add it to the running "
    "tab — do not do the math yourself. When the user asks to split the "
    "bill, call calculate_split with the number of people, the tip percent, "
    "and the tax percent. If the user mentions a country they're in, use "
    "your own knowledge of that country: pass its typical sales tax / VAT "
    "rate as tax_percent, suggest a culturally appropriate tip_percent "
    "(for example: tipping isn't customary in Japan, ~5-10% is polite in "
    "Germany, 15-20% is standard in the US), and briefly explain the local "
    "custom in your reply. If no country or tip is mentioned, use 0 for "
    "both. After a tool gives you a result, explain it back to the user in "
    "a short, friendly way — for add_expense, confirm what was added and "
    "the new running total; for calculate_split, clearly state the total "
    "and how much each person owes. Never calculate totals or splits "
    "yourself — always use the tools."
)


# ============================================================================
# THE AGENTIC LOOP
# ============================================================================
def run_bill_splitting_agent():
    print("🧾 Bill-Splitting Agent — tell me about expenses, then ask me to split "
          "the bill. Type 'quit' to exit.\n")

    messages = [{"role": "system", "content": SYSTEM_PROMPT}]

    while True:
        user_input = input("You: ").strip()
        if user_input.lower() in {"quit", "exit"}:
            print("👋 Bye!")
            break

        messages.append({"role": "user", "content": user_input})

        # ---- One user turn can take several agentic steps ------------------
        for step in range(6):
            response = client.chat.completions.create(
                model=MODEL, messages=messages, tools=tools,
            )
            ai_message = response.choices[0].message
            messages.append({
                "role": "assistant",
                "content": ai_message.content or "",
                "tool_calls": ai_message.tool_calls,
            })

            # No tool call -> the AI is giving its final answer for this turn.
            if not ai_message.tool_calls:
                print(f"\n🤖 {ai_message.content}\n")
                break

            # Otherwise, run whichever tool(s) the AI asked for.
            for tool_call in ai_message.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                print(f"   🔧 AI is using tool: {name}({args})")

                if name == "add_expense":
                    result = add_expense(args["description"], args["amount"])
                elif name == "calculate_split":
                    result = calculate_split(
                        args["num_people"],
                        args.get("tip_percent", 0),
                        args.get("tax_percent", 0),
                    )
                else:
                    result = json.dumps({"error": f"Unknown tool {name}"})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": name,
                    "content": result,
                })
        else:
            # The for loop finished all 6 steps without ever `break`-ing out
            # via a final answer — the AI was still calling tools. Let the
            # user know instead of silently doing nothing this turn.
            print("\n🤖 (I hit my 6-step limit for this turn — try asking again.)\n")


if __name__ == "__main__":
    run_bill_splitting_agent()
