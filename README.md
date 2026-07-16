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
- **Anaconda / `conda`** — a free tool that manages Python and installs the libraries the code needs.
  You set it up once, then activate it each time you work on the course.
- **`pip`** — the command that installs Python libraries (we use it to install everything in `requirements.txt`).

Whenever you see a gray box like this, it's a command to copy and paste into your terminal:

```bash
echo "Hello! I just ran my first command 🎉"
```

---

## ✅ Setup (do this once)

### Step 1 — Install Anaconda

Anaconda gives you Python plus `conda`, the tool we use to set up the course.

1. Go to **https://www.anaconda.com/download** and download the installer for your computer
   (**Mac** or **Windows**).
2. Open the installer and click through it, accepting the default options.

After it finishes, **close your terminal and open a new one** (this makes `conda` available).

> **Mac:** open the app called **Terminal**. **Windows:** open the app called **Anaconda Prompt**
> (search for it in the Start menu) — use this instead of PowerShell for the course.

Check that it worked by running:

```bash
conda --version
```

If you see a version number (like `conda 24.9.0`), you're good. ✅

### Step 2 — Get the course code onto your computer

If you were given a link to this project, download it (or "clone" it) and then move into
its folder. In the terminal:

```bash
cd vibe-coding-course
```

> `cd` means "change directory" — it's how you move into a folder in the terminal.

### Step 3 — Create your course environment and install the libraries

First, create a Python environment named **`gset-vibes`** (do this once):

```bash
conda create --name gset-vibes python=3.10 -y
```

Now **activate** it. You'll run this line every time you open a new terminal to work on
the course:

```bash
conda activate gset-vibes
```

> When it's active, you'll see `(gset-vibes)` at the start of your terminal line.

Finally, install all the AI libraries the course needs (this may take a minute the first time):

```bash
pip install -r requirements.txt
```

When it's done, everything is installed. You only re-run the `pip install` line if the
course adds new tools (or if a library ever seems missing).

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

Make sure your environment is active first (you'll see `(gset-vibes)` in your terminal). If
it isn't, run `conda activate gset-vibes`. Then run any file with `python`. For example, to
run the Class 3 Gemini examples:

```bash
python week1-foundations-text/class03-text-generation/intro_to_gemini.py
```

### Running the notebooks (the `.ipynb` files)

Notebooks let you run code one piece at a time — great for learning. To open them:

```bash
jupyter lab
```

This opens Jupyter in your web browser. Click any `.ipynb` file to open it, then press
**Shift + Enter** to run a block of code.

> Using **VS Code** or **Cursor** instead? Just open a `.ipynb` file, and when it asks which
> "kernel" or "environment" to use, pick the one named **`gset-vibes`** (the conda environment
> you made in Step 3).

---

## 🧰 Adding or changing libraries (for later)

All dependencies live in one file: `requirements.txt`. To add a new library:

1. Open `requirements.txt` and add the library's name on its own line (for example
   `matplotlib`).
2. With your environment active, install it:

```bash
pip install -r requirements.txt
```

That's it — the library is now available. Keeping everything in `requirements.txt` means
the code works the same on every computer.

---

## 🆘 Common problems

- **"conda: command not found"** — You need to close and re-open your terminal after installing
  Anaconda (Step 1). On **Windows**, use the **Anaconda Prompt** app, not PowerShell.
- **You don't see `(gset-vibes)` in your terminal** — Run `conda activate gset-vibes` before
  running any code. You have to do this each time you open a new terminal.
- **"GEMINI_API_KEY not found" or an authentication error** — Your `.env` file is missing or
  the key is wrong. Re-check Step 5, and make sure the file is named exactly `.env`.
- **A library seems missing** — Make sure your environment is active, then run
  `pip install -r requirements.txt` again.
- **Notebook won't run / wrong Python** — Pick the `gset-vibes` kernel (see the notebooks section).

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
- [Download Anaconda](https://www.anaconda.com/download)
- [conda cheat sheet](https://docs.conda.io/projects/conda/en/latest/user-guide/cheatsheet.html)

---

## 🎓 Instructor

**Niral Shah** — GSET

This course material is for educational purposes as part of the GSET program.

**Ready to vibe with AI?** 🚀 Start with Week 1 in `week1-foundations-text/`!
