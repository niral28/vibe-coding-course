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

A `.env` file is where you keep secret keys. Each project folder already has a template
called **`.env.example`** — you just make a copy of it named **`.env`** and paste in your key.

**The easy way (works everywhere):** make one `.env` in the main project folder. From the
project's main folder, run:

```bash
cp shared/.env.example .env
```

> The code looks in the current folder and then in the folders above it, so a single `.env`
> in the main project folder is found by every lesson. ✅

**Prefer one per folder?** Every folder that needs a key also has its own `.env.example`.
Copy it to `.env` right there — for example, in the Class 3 folder:

```bash
cp week1-foundations-text/class03-text-generation/.env.example week1-foundations-text/class03-text-generation/.env
```

> Not comfortable with the terminal? Just **duplicate** the `.env.example` file in your
> editor and **rename the copy to `.env`**.

Either way, open your new `.env` file and replace `your_gemini_api_key_here` with the key you
copied:

```
GEMINI_API_KEY=paste_your_real_key_here
```

Save the file. **You're all set!** 🎉 (Your `.env` stays private — it's never shared or
uploaded. Only the `.env.example` templates are.)

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

## 🐙 Setting up Git and GitHub (with SSH)

**Git** is a tool that saves snapshots of your code. **GitHub** is a website that stores
those snapshots online so you can back up your work and share it. You'll set this up once.

### Step 1 — Install Git

**On Mac:** Git usually comes with the developer tools. Open **Terminal** and run:

```bash
git --version
```

If you see a version number, you're done. If it asks to install "command line developer
tools," click **Install** and wait for it to finish.

**On Windows:** download and install **Git for Windows** from **https://git-scm.com/download/win**.
Accept the default options. When it finishes, open the app called **Git Bash** — you'll type
the commands below there.

### Step 2 — Tell Git who you are

Run these two commands (use your own name and email). This just labels your snapshots:

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Step 3 — Create a free GitHub account

1. Go to **https://github.com/signup**.
2. Pick a username, enter your email, and create a password.
3. Verify your email when GitHub sends you a confirmation.

### Step 4 — Create an SSH key

An **SSH key** is a secure "handshake" so GitHub knows it's really you — no passwords needed
each time. It comes in two parts: a **private** key (keep secret, never share) and a
**public** key (safe to share with GitHub).

In **Terminal** (Mac) or **Git Bash** (Windows), run this — use *your* GitHub email:

```bash
ssh-keygen -t ed25519 -C "you@example.com"
```

When it asks *"Enter file in which to save the key"* and *"Enter passphrase,"* just press
**Enter** each time to accept the defaults. (A passphrase is optional extra protection.)

### Step 5 — Copy your public key

**On Mac:**

```bash
pbcopy < ~/.ssh/id_ed25519.pub
```

**On Windows (Git Bash):**

```bash
cat ~/.ssh/id_ed25519.pub | clip
```

Your public key is now copied to your clipboard. ✅ (This copies the **`.pub`** file — the
*public* half. Never share the file without `.pub`.)

### Step 6 — Add the key to GitHub

1. Go to **https://github.com/settings/keys**.
2. Click **"New SSH key"**.
3. Give it a **Title** (like "My laptop"), leave Key type as **Authentication Key**, and
   **paste** your key into the big box.
4. Click **"Add SSH key"**.

### Step 7 — Test it

```bash
ssh -T git@github.com
```

The first time, type **`yes`** if it asks whether to continue. If you see a message like
*"Hi *your-username*! You've successfully authenticated,"* 🎉 you're all set.

> **Using this course code with your own GitHub repo?** When you create a repo on GitHub,
> choose the **SSH** URL (it starts with `git@github.com:`) to clone or connect it — that's
> the one your new key unlocks.

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
- [Google Antigravity — tips & tricks](docs/antigravity-tips.md) (our beginner cheat sheet for the AI code editor)
- [Download Google Antigravity](https://antigravity.google)

---

## 🎓 Instructor

**Niral Shah** — GSET

This course material is for educational purposes as part of the GSET program.

**Ready to vibe with AI?** 🚀 Start with Week 1 in `week1-foundations-text/`!
