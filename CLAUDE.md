# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a vibe coding course repository focused on teaching Python programming and AI integration with Google's Gemini API. The project contains educational materials and interactive coding exercises, with a special focus on building AI-powered games like Wordle.

## Setup and Environment

**Python Environment:**
- Dependencies are managed with `uv` via the root `pyproject.toml` (single source of truth).
- Install everything: `uv sync`
- Run any script/command in the environment: `uv run python <path/to/script.py>`
- Add or remove a package: `uv add <pkg>` / `uv remove <pkg>` (never hand-edit `uv.lock`).
- `pyproject.toml` and `uv.lock` are committed; do not delete them.

**Required Environment Variables:**
- `GEMINI_API_KEY`: Google Gemini API key (copy `shared/.env.example` to `.env` at the repo root)

## Code Architecture

**Main Components:**
- `class1/intro_to_gemini.py` - Core Gemini AI integration examples and Wordle game implementations
- `class1/intro_to_python.py` - Basic Python programming exercises
- `class1/wordle.txt` - Word list for Wordle game (2315 five-letter words)
- `class1/requirements.txt` - Python dependencies (dotenv, google-genai, openai, requests)

**Key Features:**
- **Gemini API Integration**: Uses both google-genai SDK and OpenAI-compatible endpoint
- **Interactive Wordle Game**: AI-powered Wordle implementation with function calling
- **Function Calling**: Advanced AI agent patterns with tool/function integration
- **RAG Implementation**: Word validation and game state management

## Common Development Tasks

**Run Wordle Game:**
```bash
cd class1
conda activate gemini-project
python intro_to_gemini.py
```

**Key Functions in intro_to_gemini.py:**
- `generate_gemini_response()` - Basic Gemini API calls
- `chat_with_gemini()` - Simple chat interface
- `chat_with_gemini_function_calling_with_rag()` - Full Wordle game with function calling
- `get_word_of_the_day()` - Random word selection from wordle.txt
- `validate_word()` - Wordle game logic with color-coded hints

## API Patterns

**Gemini Integration Methods:**
1. Direct google-genai SDK (recommended for simple use cases)
2. OpenAI-compatible endpoint for advanced features like function calling

**Function Calling Tools:**
- `get_user_input()` - Capture user guesses
- `validate_word()` - Check guesses and provide colored hints
- `end_game()` - Handle game completion states

## File Structure Notes

- `class1/` - Main course content and exercises
- `class2/` - Advanced topics (nanogpt_learning_exercise.py)
- Jupyter notebooks contain interactive learning materials
- Environment variables should never be committed (use .env files)