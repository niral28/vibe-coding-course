# Vibe Coding: AI Remix 🎵🤖

Welcome! This is the code for the **GSET Vibe Coding** course. Here you'll learn to
build fun AI apps (chatbots, games, image and audio tools) using Google's Gemini AI.

> **Never coded before? That's totally fine.** This guide walks you through every single
> step. Just follow along from top to bottom and copy/paste the commands exactly.

---

## 🧠 A few words you'll see a lot

- **Terminal** (also called "command line") — a text box where you type commands to your
  computer instead of clicking buttons. On **Mac**, open the app called **Terminal**. On
  **Windows**, open the app called **PowerShell**.
- **Command** — a line of text you type into the terminal and then press **Enter** to run.
- **API key** — a secret password that lets your code talk to Google's AI. You'll get one for free.
- **`uv`** — a free tool that installs everything the code needs, automatically. You only set it up once.

Whenever you see a gray box like this, it's a command to copy and paste into your terminal:

```bash
echo "Hello! I just ran my first command 🎉"
```

---

## ✅ Setup (do this once)

### Step 1 — Install `uv`

`uv` sets up the code for you so you don't have to install things one by one.

**On Mac:** copy this into your Terminal and press Enter:

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**On Windows:** copy this into PowerShell and press Enter:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After it finishes, **close the terminal and open a new one** (this makes `uv` available).
Check that it worked by running:

```bash
uv --version
```

If you see a version number (like `uv 0.10.2`), you're good. ✅

### Step 2 — Get the course code onto your computer

If you were given a link to this project, download it (or "clone" it) and then move into
its folder. In the terminal:

```bash
cd vibe-coding-course
```

> `cd` means "change directory" — it's how you move into a folder in the terminal.

### Step 3 — Install everything the code needs

Run this one command. `uv` reads the `pyproject.toml` file and installs everything for you
(this may take a minute the first time):

```bash
uv sync
```

When it's done, all the AI libraries are installed. You never have to do this again unless
the course adds new tools (then just run `uv sync` again).

### Step 4 — Get your free Google Gemini API key

1. Go to **https://aistudio.google.com/apikey**
2. Sign in with a Google account.
3. Click **"Create API key"** and copy the long string it gives you.

⚠️ **Keep this key private** — it's like a password. Never post it online or paste it into
your code directly.

### Step 5 — Save your API key in a `.env` file

A `.env` file is where you keep secret keys. There's a template you can copy:

```bash
cp shared/.env.example .env
```

Now open the new `.env` file (double-click it, or open it in your code editor) and replace
`your_gemini_api_key_here` with the key you copied:

```
GEMINI_API_KEY=paste_your_real_key_here
```

Save the file. **You're all set!** 🎉

---

## ▶️ Running the code

Because we use `uv`, put **`uv run`** in front of any command to run it with all the
libraries ready. For example, to run the Class 3 Gemini examples:

```bash
uv run python week1-foundations-text/class03-text-generation/intro_to_gemini.py
```

### Running the notebooks (the `.ipynb` files)

Notebooks let you run code one piece at a time — great for learning. To open them:

```bash
uv run jupyter lab
```

This opens Jupyter in your web browser. Click any `.ipynb` file to open it, then press
**Shift + Enter** to run a block of code.

> Using **VS Code** or **Cursor** instead? Just open a `.ipynb` file, and when it asks which
> "kernel" or "environment" to use, pick the one named **`.venv`** (that's the one `uv` made).

---

## 🧰 Adding or changing libraries (for later)

All dependencies live in one file: `pyproject.toml`. You don't edit it by hand — instead:

```bash
# Add a new library
uv add some-library-name

# Remove one
uv remove some-library-name
```

`uv` keeps a file called `uv.lock` that records the exact versions everyone should use, so
the code works the same on every computer. Both `pyproject.toml` and `uv.lock` are part of
the project — don't delete them.

---

## 🆘 Common problems

- **"uv: command not found"** — You need to close and re-open your terminal after installing
  `uv` (Step 1). If it still fails, run the install command again.
- **"GEMINI_API_KEY not found" or an authentication error** — Your `.env` file is missing or
  the key is wrong. Re-check Step 5, and make sure the file is named exactly `.env`.
- **A library seems missing** — Run `uv sync` again to make sure everything is installed.
- **Notebook won't run / wrong Python** — Pick the `.venv` kernel (see the notebooks section).

---

## 🗓️ What's in this course

- **Duration:** 3 weeks, 12 classes
- **For:** High schoolers — **no coding experience needed**
- **You'll build:** text chatbots, an AI Wordle game, image & audio tools, and a final project

| Week | Folder | What you'll learn |
| ---- | ------ | ----------------- |
| 1 | `week1-foundations-text/` | Python basics, the Gemini API, chatbots, function calling |
| 2 | `week2-image-audio/` | Generating images and audio, MCP tools |
| 3 | `week3-multimodal-demos/` | Code generation, final projects, demo day |

Complete, ready-to-read examples live in `example-projects/` (an AI Wordle web game and a
voice-enabled web browsing agent).

---

## 📖 Handy links

- [Get a Gemini API key](https://aistudio.google.com/apikey)
- [Gemini API docs](https://ai.google.dev/gemini-api/docs)
- [What's new in Gemini 3.5](https://ai.google.dev/gemini-api/docs/whats-new-gemini-3.5)
- [uv documentation](https://docs.astral.sh/uv/)

---

## 🎓 Instructor

**Niral Shah** — GSET

This course material is for educational purposes as part of the GSET program.

**Ready to vibe with AI?** 🚀 Start with Week 1 in `week1-foundations-text/`!
