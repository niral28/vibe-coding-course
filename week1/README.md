# Getting Started with Python, Gemini AI, and GitHub 🚀

Welcome to your first coding adventure! This guide will help you set up Python, learn some basics, connect to Google's Gemini AI, and share your code on GitHub. Don't worry if you're new to coding - we'll go step by step!

## What You'll Learn
- How to install Python and Git on your computer
- Basic Python programming concepts
- How to use Google's Gemini AI in your code
- How to save and share your code on GitHub

---

## 1. Installing Python, Git, and Visual Studio Code 🐍

### Installing Visual Studio Code (Your Code Editor)

First, let's install VS Code - this is where you'll write your code! It's like Microsoft Word, but for programmers.

**Windows & Mac:**
1. Go to [code.visualstudio.com](https://code.visualstudio.com)
2. Click "Download for Windows" or "Download for Mac"
3. Run the installer and follow the steps
4. Launch VS Code when installation is complete

**Recommended VS Code Extensions:**
Once VS Code is open, click the Extensions icon (puzzle piece) on the left sidebar and install:
- **Python** (by Microsoft) - Helps with Python coding
- **Python Debugger** (by Microsoft) - Helps find and fix errors
- **Code Runner** - Lets you run code with a click

### Installing Python

**Windows:**
1. Go to [python.org](https://python.org)
2. Click "Download Python" (get the latest version)
3. Run the installer and **CHECK THE BOX** that says "Add Python to PATH"
4. Click "Install Now"

**Mac:**
1. Go to [python.org](https://python.org)
2. Download Python for macOS
3. Run the installer and follow the steps

**Check if Python is installed:**
Open your terminal (Command Prompt on Windows, Terminal on Mac) and type:
```bash
python --version
```
You should see something like "Python 3.11.0" or similar.

### Installing Git

**Windows:**
1. Go to [git-scm.com](https://git-scm.com)
2. Download Git for Windows
3. Run the installer (you can use all default settings)

**Mac:**
Git might already be installed! Try typing `git --version` in Terminal. If not:
1. Go to [git-scm.com](https://git-scm.com)
2. Download Git for macOS
3. Run the installer

**Check if Git is installed:**
```bash
git --version
```

---

## 2. Python Basics 🎯

Let's learn some fundamental Python concepts with examples you can try!

### Variables
Variables are like containers that store data:

```python
# String (text)
name = "Alex"
favorite_color = "blue"

# Numbers
age = 16
height = 5.8

# Boolean (True/False)
is_student = True

print(f"Hi, I'm {name}! I'm {age} years old.")
```

### Strings
Strings are text data. Here are some cool things you can do:

```python
message = "Hello, World!"
print(message.upper())  # HELLO, WORLD!
print(message.lower())  # hello, world!
print(len(message))     # 13 (length of the string)

# String formatting
name = "Sarah"
age = 17
intro = f"My name is {name} and I'm {age} years old."
print(intro)
```

### Loops
Loops let you repeat code multiple times:

```python
# For loop - repeat a specific number of times
for i in range(5):
    print(f"This is loop number {i}")

# For loop with a list
fruits = ["apple", "banana", "orange"]
for fruit in fruits:
    print(f"I like {fruit}")

# While loop - repeat while a condition is true
count = 0
while count < 3:
    print(f"Count is {count}")
    count += 1
```

### Try it yourself!
Create a file called `python_practice.py` and experiment with these concepts!

**How to create and run a Python file in VS Code:**
1. Open VS Code
2. Click "File" → "New File"
3. Save it as `python_practice.py` (the .py extension tells VS Code it's Python)
4. Write some Python code
5. Right-click in the editor and select "Run Python File in Terminal"
6. Or use the play button in the top-right corner if you installed Code Runner

---

## 3. Gemini SDK Setup 🤖

Now let's set up Google's Gemini AI so you can build AI-powered apps!

### Step 1: Get your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key and save it somewhere safe!

### Step 2: Install the Gemini SDK
Open your terminal and run:
```bash
pip install google-generativeai
```

### Step 3: Set up your environment
Create a new file called `.env` in your project folder:
```
GEMINI_API_KEY=your_api_key_here
```
Replace `your_api_key_here` with your actual API key.

**Important:** Never share your API key publicly or commit it to GitHub!

---

## 4. Hello World with Gemini 🌟

Let's create your first AI-powered program!

Create a file called `gemini_hello.py`:

```python
import google.generativeai as genai
import os

# Configure the API key
# For now, we'll put the key directly in the code
# (In real projects, use environment variables)
api_key = "YOUR_API_KEY_HERE"  # Replace with your actual key
genai.configure(api_key=api_key)

# Create a model instance
model = genai.GenerativeModel('gemini-pro')

# Simple chat completion
def chat_with_gemini(prompt):
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"Error: {e}"

# Test it out!
if __name__ == "__main__":
    print("🤖 Welcome to Gemini Chat!")
    print("Type 'quit' to exit\n")
    
    while True:
        user_input = input("You: ")
        if user_input.lower() == 'quit':
            print("Goodbye!")
            break
        
        response = chat_with_gemini(user_input)
        print(f"Gemini: {response}\n")
```

### How to run it:
1. Open VS Code
2. Create a new file and save it as `gemini_hello.py`
3. Copy and paste the code above
4. Replace `YOUR_API_KEY_HERE` with your actual API key
5. Right-click in the editor and select "Run Python File in Terminal"
6. Start chatting with AI!

### What's happening in the code:
- We import the Gemini library
- We configure it with our API key
- We create a model instance
- We make a function that sends prompts to Gemini and gets responses
- We create a simple chat loop

---

## 5. GitHub - Share Your Code 🐙

GitHub is like Google Drive for code! Let's learn how to save and share your projects.

### Step 1: Create a GitHub Account
1. Go to [github.com](https://github.com)
2. Click "Sign up"
3. Choose a username (this will be public!)
4. Verify your email

### Step 2: Create Your First Repository
1. Click the "+" button in the top-right corner
2. Select "New repository"
3. Name it something like "my-first-gemini-project"
4. Add a description like "My first AI project with Python and Gemini"
5. Make it public (so others can see your awesome work!)
6. Check "Add a README file"
7. Click "Create repository"

### Step 3: Set up Git on your computer
In your terminal, configure Git with your info:
```bash
git config --global user.name "Your Name"
git config --global user.email "your.email@example.com"
```

### Step 4: Clone your repository
1. On your GitHub repository page, click the green "Code" button
2. Copy the HTTPS URL
3. In your terminal, navigate to where you want to save your project
4. Run:
```bash
git clone https://github.com/yourusername/my-first-gemini-project.git
```

### Step 5: Add your code and commit changes
1. Move your Python files into the cloned folder
2. In your terminal, navigate to the project folder
3. Add your files:
```bash
git add .
```
4. Commit your changes:
```bash
git commit -m "Add my first Gemini AI chat program"
```
5. Push to GitHub:
```bash
git push origin main
```

### Understanding Git commands:
- `git add .` - Stages all your changes (gets them ready to save)
- `git commit -m "message"` - Saves your changes with a description
- `git push origin main` - Uploads your changes to GitHub

---

## 🎉 Congratulations!

You've just:
- ✅ Installed Python and Git
- ✅ Learned basic Python concepts
- ✅ Set up the Gemini AI SDK
- ✅ Created your first AI chat program
- ✅ Shared your code on GitHub

## Next Steps
- Experiment with different prompts in your Gemini chat
- Try adding features like saving chat history
- Learn about Python functions and classes
- Explore other AI models and APIs
- Build more complex projects!

## Resources
- [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- [Google AI Studio](https://makersuite.google.com/)
- [GitHub Guides](https://guides.github.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)

## Need Help?
- Ask questions in coding communities like Stack Overflow
- Check out Python and AI tutorials on YouTube
- Don't be afraid to experiment - coding is about learning by doing!

Remember: Every expert was once a beginner. Keep coding and have fun! 🚀