# Google Antigravity — Tips & Tricks 🚀

**Google Antigravity** is Google's free **agentic IDE** (code editor) powered by Gemini 3.
Instead of only *chatting* with an AI, you give it a goal and it works like a teammate — it
can write code across multiple files, run commands, open a browser, and hand you back
"artifacts" (a plan, screenshots, a task list) so you can check its work.

It's a great tool for this course. This page is a friendly cheat sheet to get you productive
fast.

> **New to all this?** You don't *need* Antigravity to finish the course — VS Code or Cursor
> work fine. But it's a fun, powerful way to "vibe code," so it's worth trying.

---

## 🛠️ Getting started

1. **Download it** from **https://antigravity.google** and install for your OS (Windows,
   macOS, or Linux).
2. **Sign in with your class Google Cloud account.** For this course we use Antigravity
   through a shared **Google Cloud project** (not the personal free-Gmail preview), so:
   - Choose the sign-in option that uses your **Google Cloud / Google Workspace account**,
     and sign in with the **Google account your instructor added to the class project**.
   - If you're asked to **pick a project**, select our class project:
     **`gset-soe-dean-antoine`**.
   - Access, billing, and model usage are handled through that project — so you **don't need
     your own API key or credit card** for Antigravity.

   > 📌 Use the **Google account your instructor added** to the `gset-soe-dean-antoine`
   > project. If sign-in says you don't have access, ask them to confirm you've been added.
3. On first launch you can **import your settings** from VS Code or Cursor, so it feels
   familiar right away.
4. **Open this course folder** (`vibe-coding-course`) in Antigravity, just like any editor.

> Make sure your `gset-vibes` conda environment and `.env` file are set up first (see the
> main [README](../README.md)). Antigravity runs your code the same way — it just helps you
> *write* it.

---

## 🧠 The two main views

Antigravity has two ways to work. Switch between them depending on the task:

- **Editor View** — a normal, hands-on code editor with AI autocomplete and inline commands.
  Best when *you* are driving and want small suggestions.
- **Agent Manager (Manager Surface)** — a dashboard where you launch one or more **agents**
  that go off and do larger tasks on their own while you watch. Best when you want to say
  "build me X" and review the result.

---

## ⚡ Tips & tricks

1. **Pick the right mode for the job.** Use **Fast** mode for quick edits and small
   questions; use **Planning** mode for bigger tasks — the agent writes a plan you can read
   and approve *before* it changes your code. For beginners, Planning mode is a great way to
   learn, because you get to see the AI's thinking.

2. **Read the Artifacts.** When an agent finishes, it produces artifacts — a task list, an
   implementation plan, screenshots, even a browser recording. **Skim these to verify the
   work** instead of blindly trusting the code. This is the single best habit to build.

3. **Keep tasks small and specific.** "Add a score counter to the Wordle game and show it
   after each guess" works far better than "make the game better." Specific asks = better
   results.

4. **Set custom rules so you don't repeat yourself.** Add a `.md` file under `.agent/rules/`
   with standing instructions the AI always follows — e.g. *"Always read the Gemini key from
   `.env` with python-dotenv; never paste keys inline"* or *"Explain new code in simple terms
   for a beginner."* Great for keeping the AI aligned with how this course does things.

5. **Handy keyboard shortcuts:**
   - Toggle the **terminal** panel: `` Ctrl + ` ``
   - Toggle the **agent** panel: `Cmd + L` (Mac) / `Ctrl + L` (Windows)

6. **Choose an autonomy level you're comfortable with.** When setting up, "Agent-Assisted"
   lets the agent run commands but *asks you before big changes*. Good default while you're
   learning — you stay in the loop.

7. **Run agents in parallel (when you're ready).** The Agent Manager can run multiple agents
   in separate workspaces at once — e.g. one fixing a bug while another writes a README. Come
   back to this once you're comfortable with a single agent.

8. **Always test what the AI writes.** Run your program and try it yourself. AI is fast but
   not perfect — running the code is how you catch mistakes. (This is the "verify" habit from
   class!)

9. **When a model name errors, update it.** Model names change over time. If code the agent
   wrote uses an old model, swap in a current one from the
   [Gemini models list](https://ai.google.dev/gemini-api/docs/models).

---

## 🔗 Learn more

- [Download Antigravity](https://antigravity.google)
- [Getting Started codelab (Google)](https://codelabs.developers.google.com/getting-started-google-antigravity)
- [Google Developers Blog — Build with Antigravity](https://developers.googleblog.com/build-with-google-antigravity-our-new-agentic-development-platform/)
- [Antigravity Editor Tips & Tricks (Mete Atamel)](https://atamel.dev/posts/2025/12-01_antigravity_editor_tips/)
- [15 Essential Antigravity Tips (DEV Community)](https://dev.to/czmilo/15-essential-google-antigravity-tips-and-tricks-complete-guide-in-2025-3omj)
