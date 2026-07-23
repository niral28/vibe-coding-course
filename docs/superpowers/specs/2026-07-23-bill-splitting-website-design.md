# Bill-Splitting Agent Website — Design

**Date:** 2026-07-23
**Location:** `week1-foundations-text/class05-function-calling-agents/`

## Goal

Turn the working terminal program `bill_splitting_agent.py` into a clean web page
that keeps the same tools and agentic loop, visually announces every Gemini API
call and loop step, adds country-aware tax/tipping via Gemini's own knowledge,
and explains the code simply to students.

## Architecture

- **New file `bill_splitting_web.py`** — a Flask app in the class05 folder.
- **New file `static/index.html`** — the entire frontend (one self-contained
  page: HTML + CSS + vanilla JS, no build step).
- **`bill_splitting_agent.py` keeps working unchanged as a terminal program.**
  The web app imports `add_expense`, `calculate_split`, `tools`, and `client`
  from it so there is one source of truth for the tools.
- **Flow:** browser POSTs the chat message → Flask runs the same agentic loop
  (max 6 steps per turn) → each step is **streamed live to the browser via
  server-sent events (SSE)**: `api_call`, `tool_call`, `tool_result`,
  `final_answer`, `error` events. The console shows real round-trips as they
  happen, not a replay.
- `GEMINI_API_KEY` stays in `.env` on the server; the browser never sees it.
- Single-user, in-memory session state (the `expenses` list), matching the
  terminal version. A "Reset tab" button clears expenses and the conversation.

## Tool changes (same tools, one small extension)

- `add_expense(description, amount)` — untouched.
- `calculate_split(num_people, tip_percent=0, tax_percent=0)` — gains an
  optional `tax_percent`; the returned JSON adds `tax_amount` and includes tax
  in `total`. Tool schema updated to match.
- **System prompt extension:** if the user mentions a country, Gemini uses its
  own knowledge of that country's sales tax/VAT and tipping culture — it passes
  the tax rate and a culturally appropriate tip to `calculate_split` and
  briefly explains the custom (e.g. "In Japan tipping isn't customary, so I
  used 0%"). No new tool and no hardcoded country table: this is where the API
  is "put to use".
- Terminal version's prompt/tool schema updated identically so both stay in sync.

## The page

- **Header:** app name + one-line explanation.
- **Left — chat panel:** user/AI bubbles; small inline tool-call chips
  mirroring the terminal's `🔧 AI is using tool` lines; a running-tab card
  listing current expenses and the total; hint chip under the input:
  *"💡 Tip: mention a country — 'we're in Japan' — and I'll apply local tax &
  tipping customs."*
- **Right — Agent Console (star feature):** live numbered timeline per turn:
  `📤 Calling Gemini API (request #1)` (pulsing badge with model name) →
  `🔧 Tool call: add_expense({...})` → `📥 Tool result` →
  `📤 Calling Gemini API (request #2)` → `💬 Final answer`. Numbered requests
  make the loop visible: one user message, several API round-trips.
- **Bottom — "How it works":** three short cards explaining the code simply:
  ① Function calling (the AI doesn't do math — it asks Python to),
  ② The agentic loop (keep calling Gemini until it stops asking for tools),
  ③ The tools themselves, showing the actual tool definitions.
- Clean, modern, single screen; responsive enough for a projector demo.

## Error handling

- Missing/invalid `GEMINI_API_KEY` → friendly banner on the page, no crash.
  (The agent module reads the key at import time, so the web app checks for
  the key first and only imports the agent module when it's present.)
- Gemini/network errors → red `error` step in the Agent Console.
- Unknown tool name → error JSON returned to the model (as in the terminal
  version).

## Testing

- Extend `test_bill_splitting.py` with `tax_percent` math checks — still pure
  math, no API key needed.
- End-to-end: run the Flask app, exercise in the browser (add expenses,
  mention a country, split, reset).
- Add `flask` to the root `requirements.txt`.

## Out of scope

- Multi-user sessions, persistence, auth, deployment — this is a local class
  demo run with `python bill_splitting_web.py`.
