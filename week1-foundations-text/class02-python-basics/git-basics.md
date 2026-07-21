# Git Basics

A beginner-friendly guide to Git — the tool that tracks changes to your code so you can save your progress, undo mistakes, and collaborate with others.

## What is Git?

**Git** is a *version control system*. Think of it as a "save history" for your entire project:

- 📸 It takes **snapshots** (called *commits*) of your files whenever you tell it to.
- ⏪ You can **go back** to any previous snapshot if something breaks.
- 👥 It lets **multiple people** work on the same project without overwriting each other's work.

> **Git vs. GitHub:** Git is the tool that runs on your computer. [GitHub](https://github.com) is a website that stores your Git projects online so you can back them up and share them.

## Core Concepts

| Term | What it means |
|------|---------------|
| **Repository (repo)** | A folder that Git is tracking. Contains all your files + their history. |
| **Commit** | A saved snapshot of your changes, with a message describing what you did. |
| **Branch** | A separate line of work. `main` is the default branch. |
| **Remote** | A copy of your repo hosted online (e.g., on GitHub). Usually called `origin`. |
| **Staging area** | A "waiting room" where you pick which changes go into your next commit. |

## The Everyday Workflow

The three steps you'll use most often:

```bash
# 1. Stage your changes (pick what to save)
git add .

# 2. Commit them (save a snapshot with a message)
git commit -m "Add my first Python script"

# 3. Push to GitHub (upload your changes)
git push
```

Here's how a change moves through Git:

```
Working Directory  →  Staging Area  →  Repository  →  Remote (GitHub)
   (git add)            (git commit)      (git push)
```

## Getting Started

### First-time setup (only once per computer)

```bash
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

### Starting a project

```bash
# Option A: Create a brand-new repo in the current folder
git init

# Option B: Copy an existing repo from GitHub
git clone https://github.com/username/repo-name.git
```

## Essential Commands

### Checking status and history

```bash
git status        # What's changed? What's staged?
git log           # See the history of commits
git log --oneline # A compact, one-line-per-commit view
git diff          # See exactly what you changed (not yet staged)
```

### Saving changes

```bash
git add filename.py    # Stage one specific file
git add .              # Stage ALL changed files
git commit -m "message"  # Commit staged changes with a message
```

### Working with GitHub (remotes)

```bash
git push               # Upload your commits to GitHub
git pull               # Download the latest changes from GitHub
git clone <url>        # Copy a repo from GitHub to your computer
```

## Branching

Branches let you try new ideas without breaking your working code.

```bash
git branch                 # List all branches
git checkout -b my-feature # Create AND switch to a new branch
git checkout main          # Switch back to the main branch
git merge my-feature       # Merge my-feature into your current branch
```

## Undoing Things

Everyone makes mistakes — Git makes them fixable.

```bash
# Unstage a file (keep the changes, just remove from staging)
git restore --staged filename.py

# Discard changes to a file (⚠️ can't undo this!)
git restore filename.py

# Change your last commit message
git commit --amend -m "New message"
```

## Writing Good Commit Messages

A good commit message tells the story of *why* a change was made.

| ✅ Good | ❌ Not helpful |
|---------|---------------|
| `Add input validation to Wordle guesses` | `stuff` |
| `Fix crash when word list is empty` | `fixed it` |
| `Update README with setup instructions` | `asdf` |

**Tips:**
- Keep it short (under ~50 characters for the summary).
- Use the present tense: "Add feature" not "Added feature".
- Describe *what* the change does, not just *that* you changed something.

## A `.gitignore` File

Some files shouldn't be tracked by Git — like secrets, or auto-generated files. List them in a `.gitignore` file:

```gitignore
# Never commit your API keys!
.env

# Python cache files
__pycache__/
*.pyc

# Virtual environments
venv/
```

> 🔒 **Important:** Never commit your `GEMINI_API_KEY` or any secrets. Always keep them in a `.env` file that's listed in `.gitignore`.

## Using Git in VS Code (No Terminal Needed!)

VS Code has Git built right in, so you can do everything above by clicking buttons instead of typing commands. This is often easier when you're starting out.

### The Source Control panel

Click the **Source Control** icon in the left sidebar (it looks like a branching line 🔀), or press:

- **Mac:** `Cmd` + `Shift` + `G`
- **Windows/Linux:** `Ctrl` + `Shift` + `G`

This panel shows every file you've changed since your last commit.

### Committing changes (the VS Code way)

1. **Make your changes** and save your files (`Cmd/Ctrl` + `S`).
2. Open the **Source Control** panel — your changed files appear under "Changes".
3. **Stage a file** by hovering over it and clicking the **`+`** icon. (Or click the `+` next to "Changes" to stage everything — same as `git add .`)
4. **Type a commit message** in the box at the top.
5. Click the **✓ Commit** button (or press `Cmd/Ctrl` + `Enter`).

> 💡 Each step maps to a command you already learned: staging = `git add`, the ✓ button = `git commit`.

### Pushing and pulling

After committing, send your work to GitHub:

- Click the **`...`** menu (or the **Sync Changes** button) → **Push** to upload.
- Use **Pull** to download the latest changes from GitHub.
- The **🔄 Sync Changes** button does a pull *and* a push in one click.

You can also see push/pull status in the **bottom-left corner** of VS Code, next to the branch name.

### Signing in to GitHub

The first time you push, VS Code will ask you to **sign in to GitHub** in your browser. Click **Allow** / **Authorize**, and VS Code remembers you from then on — no passwords to type each time.

### Switching branches

Click the **branch name** in the bottom-left corner of VS Code. A menu pops up where you can:

- Switch to another branch
- Create a new branch (`+ Create new branch...`)

### Helpful extension

Install the **GitLens** extension (from the Extensions panel) to see *who* changed each line and *when*, right inside your code. Great for understanding project history.

### Terminal vs. VS Code buttons — which should I use?

| | Terminal | VS Code buttons |
|---|----------|-----------------|
| **Best for** | Learning how Git really works, speed | Visual clarity, avoiding typos |
| **You type** | Commands | Nothing — just click |

Both do the *exact same thing* under the hood. Use whichever feels comfortable — many people mix both!

## Quick Reference Cheat Sheet

```bash
git init                       # Start tracking a project
git clone <url>                # Copy a repo from GitHub
git status                     # Check what's changed
git add .                      # Stage all changes
git commit -m "message"        # Save a snapshot
git push                       # Upload to GitHub
git pull                       # Download from GitHub
git log --oneline              # View commit history
git checkout -b <branch>       # Create a new branch
git merge <branch>             # Merge a branch in
```

## Learn More

- [GitHub's Git Handbook](https://guides.github.com/introduction/git-handbook/)
- [Interactive Git tutorial](https://learngitbranching.js.org/)
- [Official Git documentation](https://git-scm.com/doc)

---

*Happy committing! 🚀 Remember: commit early, commit often.*
