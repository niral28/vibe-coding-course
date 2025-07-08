# Getting Started with Python, Gemini AI, and GitHub 🚀

Welcome to your first coding adventure! This guide will help you set up Python, learn some basics, connect to Google's Gemini AI, and share your code on GitHub. Don't worry if you're new to coding - we'll go step by step!

## What You'll Learn
- How to install Python and Git on your computer
- Basic Python programming concepts
- How to use Google's Gemini AI in your code
- How to save and share your code on GitHub

---

## 1. Installing Miniconda, Git, and Cursor 🐍

### Installing Cursor (Your AI-Powered Code Editor)

We're going to use Cursor - it's like having a smart coding assistant built right into your editor! Perfect for our vibe coding approach.

**Windows & Mac:**
1. Go to [cursor.sh](https://cursor.sh)
2. Click "Download for Windows" or "Download for Mac"
3. Run the installer and follow the steps
4. Launch Cursor when installation is complete

**Why Cursor is perfect for this course:**
- **Built-in AI chat** - Ask questions about your code without leaving the editor
- **Smart suggestions** - AI helps you write code faster
- **Error explanations** - When something breaks, AI can explain what went wrong
- **Modern vibe** - This is how coding feels in 2025!

**Recommended Cursor Extensions:**
Once Cursor is open, click the Extensions icon (puzzle piece) on the left sidebar and install:
- **Python** (by Microsoft) - Helps with Python coding
- **Python Debugger** (by Microsoft) - Helps find and fix errors
- **Code Runner** - Lets you run code with a click

**Pro tip:** Try pressing `Ctrl+L` (or `Cmd+L` on Mac) to open the AI chat panel - you can ask it questions about your code anytime!

### Installing Miniconda (Python + Package Manager)

Instead of installing Python directly, we'll use Miniconda. This gives us Python AND helps us manage different projects cleanly (like having separate folders for different school subjects).

**Why Miniconda?**
- Avoids conflicts with any Python already on your computer
- Lets you create separate "environments" for different projects
- Makes installing packages much easier
- This is how professional developers work!

**Windows:**
1. Go to [docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
2. Download "Miniconda3 Windows 64-bit"
3. Run the installer
4. When asked, check "Add Miniconda3 to my PATH environment variable"
5. Complete the installation

**Mac:**
1. Go to [docs.conda.io/en/latest/miniconda.html](https://docs.conda.io/en/latest/miniconda.html)
2. Download "Miniconda3 macOS 64-bit pkg"
3. Run the installer and follow the steps

**Check if conda is installed:**
Open your terminal (Command Prompt on Windows, Terminal on Mac) and type:
```bash
conda --version
```
You should see something like "conda 23.x.x" or similar.

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
### Creating Your First Python Environment

Now let's create a special space for your AI project. Think of this like creating a dedicated folder for a school project - it keeps everything organized and separate.

**Create a new environment:**
```bash
conda create -n gemini-project python=3.11
```

**Activate your environment:**
```bash
conda activate gemini-project
```

Your terminal prompt should now show `(gemini-project)` at the beginning - this means you're in your special Python environment!

**Important:** You'll need to activate this environment every time you work on this project. It's like opening the right folder for your homework.

**To deactivate later (when you're done coding):**
```bash
conda deactivate
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

### Fun Challenge: Drawing Shapes with Code! 🎨

Let's use loops to create cool patterns. This is where coding gets creative!

**Square Pattern:**
```python
# Draw a 5x5 square
size = 5
for i in range(size):
    print("* " * size)
```

**Triangle Pattern:**
```python
# Draw a triangle
height = 5
for i in range(1, height + 1):
    print("* " * i)
```

**Diamond Pattern (Challenge!):**
```python
# Draw a diamond - this one's tricky!
size = 5

# Top half (including middle)
for i in range(1, size + 1):
    spaces = " " * (size - i)
    stars = "* " * i
    print(spaces + stars)

# Bottom half
for i in range(size - 1, 0, -1):
    spaces = " " * (size - i)
    stars = "* " * i
    print(spaces + stars)
```

**Your Turn - Shape Challenges:**
Try creating these shapes (use Cursor's AI if you get stuck!):

1. **Right Triangle:** A triangle that leans to the right
2. **Hollow Square:** A square that's empty in the middle
3. **Christmas Tree:** A triangle with a trunk at the bottom
4. **Heart Shape:** Get creative with this one!

**Cursor AI Tip:** If you want to try these challenges, ask Cursor's AI: "Can you help me draw a [shape name] using Python loops and print statements?"

### Try it yourself!
Create a file called `python_practice.py` and experiment with these concepts!

**How to create and run a Python file in Cursor:**
1. Open Cursor
2. Click "File" → "New File"
3. Save it as `python_practice.py` (the .py extension tells Cursor it's Python)
4. Write some Python code
5. Right-click in the editor and select "Run Python File in Terminal"
6. Or use the play button in the top-right corner if you installed Code Runner

**Cursor AI tip:** If you get stuck, press `Ctrl+L` (or `Cmd+L` on Mac) and ask the AI: "Can you explain what this code does?" or "Why am I getting an error?"

---

## 3. Gemini SDK Setup 🤖

Now let's set up Google's Gemini AI so you can build AI-powered apps!

### Step 1: Get your API Key
1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy your API key and save it somewhere safe!

### Step 2: Install the Gemini SDK
Make sure your gemini-project environment is activated first:
```bash
conda activate gemini-project
```

Then install the Gemini SDK:
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
1. Make sure your environment is activated:
```bash
conda activate gemini-project
```
2. Open Cursor
3. Create a new file and save it as `gemini_hello.py`
4. Copy and paste the code above
5. Replace `YOUR_API_KEY_HERE` with your actual API key
6. Right-click in the editor and select "Run Python File in Terminal"
7. Start chatting with AI!

**Cursor AI tip:** If you run into any issues, press `Ctrl+L` (or `Cmd+L` on Mac) and ask the AI: "I'm getting an error with my Gemini API setup, can you help me debug this?"

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
- ✅ Installed Cursor (with AI superpowers!), Miniconda, and Git
- ✅ Created your first Python environment (like a pro!)
- ✅ Learned basic Python concepts
- ✅ Set up the Gemini AI SDK
- ✅ Created your first AI chat program
- ✅ Shared your code on GitHub

## Important Reminders
- **Always activate your environment** before working on this project: `conda activate gemini-project`
- **Keep your API key secret** - never share it or commit it to GitHub
- **Use Cursor's AI chat** - Press `Ctrl+L` (or `Cmd+L` on Mac) whenever you need help
- **Practice regularly** - coding is like learning a musical instrument!

## Next Steps
- Experiment with different prompts in your Gemini chat
- Try asking Cursor's AI to help you add features like saving chat history
- Learn about Python functions and classes (ask Cursor to explain!)
- Explore other AI models and APIs
- Build more complex projects with AI assistance!

## Resources
- [Python.org Tutorial](https://docs.python.org/3/tutorial/)
- [Google AI Studio](https://makersuite.google.com/)
- [GitHub Guides](https://guides.github.com/)
- [Gemini API Documentation](https://ai.google.dev/docs)
- [Cursor Documentation](https://cursor.sh/docs)

## Need Help?
- **First:** Try asking Cursor's AI chat (`Ctrl+L` or `Cmd+L`) - it's surprisingly good!
- Ask questions in coding communities like Stack Overflow
- Check out Python and AI tutorials on YouTube
- Don't be afraid to experiment - coding is about learning by doing!

Remember: Every expert was once a beginner. Keep coding, keep vibing, and have fun! 🚀✨