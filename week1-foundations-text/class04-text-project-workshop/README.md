# Class 4 Project — World Cup Hype Card ⚽🔥

In this project you'll build a program that uses AI to **hype up a World Cup final**.
You pick two teams, and Gemini:

1. Writes an energetic hype paragraph, fun facts, and a score prediction.
2. Draws a match poster and saves it as `poster.png`.

This is your first "mini project" — it puts together everything from Class 3 (talking to
Gemini) plus a brand-new trick: **making images**.

---

## ✅ What you need

You already set these up in the main [README](../../README.md) — you don't need to do
anything new:

- The `gset-vibes` environment, active in your terminal (you'll see `(gset-vibes)`).
- The course libraries from `requirements.txt` (this project uses `google-genai` and
  `pillow`).
- Your Gemini API key saved in the `.env` file. The program reads it automatically, so you
  **never paste your key into the code**.

If you're missing any of those, follow Steps 3–5 in the main README.

---

## ▶️ How to run it

From the project's main folder, with `(gset-vibes)` active:

```bash
python week1-foundations-text/class04-text-project-workshop/world_cup_hype_card.py
```

The hype text prints in your terminal, and the poster is saved as **`poster.png`** in the
folder you ran the command from. Open it to see your card!

---

## 🛠️ Make it yours (stretch goals)

Once the basic version works, try these — each one is a small change to the code:

1. **Pick your own teams.** Change `TEAM_A` and `TEAM_B` near the top of the file.
2. **Change the vibe.** Edit the `prompt` in `get_hype_text` — make it dramatic, funny, or
   write it as a rap.
3. **Restyle the poster.** Edit the `art_prompt` in `make_poster` — try "retro 1980s style",
   "comic book style", or "watercolor painting".
4. **Ask the user for the teams.** Replace the fixed `TEAM_A`/`TEAM_B` with `input()` so the
   program asks who's playing when it runs.
5. **Add a team.** Make a group-stage card with three or four teams instead of two.
6. **Name the poster after the teams.** Change the `filename` so it saves as, for example,
   `Argentina_vs_France.png`.

---

## 🆘 Common problems

- **"GEMINI_API_KEY not found" / authentication error** — Your `.env` file is missing or the
  key is wrong. Re-check Step 5 in the main README.
- **A model name error** — Model names change over time. Check the current text and image
  models at the [Gemini API docs](https://ai.google.dev/gemini-api/docs/models) and update
  `TEXT_MODEL` / `IMAGE_MODEL` at the top of the file.
- **"No image came back this time"** — Just run it again, or tweak the `art_prompt`. Image
  models occasionally return only text.
