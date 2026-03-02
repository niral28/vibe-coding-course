# Shared Resources 🔧

This directory contains utilities, configurations, and resources shared across all weeks and projects.

---

## Files

### 🔑 `.env.example`
**Environment variable template**

Copy this file to create your own `.env`:
```bash
cp .env.example .env
```

Then edit `.env` and add your API keys:
```bash
GEMINI_API_KEY=your_actual_api_key_here
OPENAI_API_KEY=your_openai_key_if_needed
```

⚠️ **Never commit `.env` files to Git!** They contain sensitive API keys.

---

### 📦 `requirements.txt`
**Master Python dependencies file**

Contains all packages needed for the course:
- `python-dotenv` - Environment variable management
- `google-genai` - Google Gemini API
- `openai` - OpenAI API (optional)
- `flask` - Web framework
- `requests` - HTTP library
- And more...

Install all dependencies:
```bash
pip install -r requirements.txt
```

---

### 📁 `utils/`
**Shared utility functions**

Common helper functions used across projects:
- API wrappers
- Text processing utilities
- File I/O helpers
- Configuration loaders

(Coming soon - will be populated as patterns emerge)

---

## Getting Your API Keys

### Google Gemini API Key

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key and paste it in your `.env` file

**Free tier includes**:
- 15 requests per minute
- 1 million tokens per minute
- 1,500 requests per day

---

### OpenAI API Key (Optional)

1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Sign in or create account
3. Navigate to API Keys section
4. Create new secret key
5. Copy and save securely

**Note**: OpenAI requires payment setup, but includes free trial credits.

---

## Environment Setup Best Practices

### 1. Use Virtual Environments
```bash
# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Use Conda (Recommended for this course)
```bash
# Create environment
conda create -n gemini-project python=3.11

# Activate it
conda activate gemini-project

# Install dependencies
pip install -r requirements.txt
```

### 3. Keep API Keys Secure
- ✅ Use `.env` files
- ✅ Add `.env` to `.gitignore`
- ✅ Never hardcode keys in source code
- ✅ Use environment variable loading libraries
- ❌ Never commit API keys to Git
- ❌ Never share keys publicly

---

## Common Utilities Pattern

### Loading Environment Variables
```python
from dotenv import load_dotenv
import os

# Load .env file
load_dotenv()

# Access API key
api_key = os.getenv("GEMINI_API_KEY")
```

### Making API Calls
```python
import google.generativeai as genai

# Configure API
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

# Create model
model = genai.GenerativeModel('gemini-2.0-flash-exp')

# Generate response
response = model.generate_content("Hello, AI!")
print(response.text)
```

---

## Troubleshooting

### "Module not found" errors
```bash
# Make sure you've installed requirements
pip install -r requirements.txt

# Verify you're in the right environment
which python  # Should point to venv/bin/python or conda env
```

### "API key not valid" errors
```bash
# Check .env file exists
ls -la | grep .env

# Verify API key is set
echo $GEMINI_API_KEY  # Should show your key

# In Python, check:
import os
print(os.getenv("GEMINI_API_KEY"))  # Should not be None
```

### Port already in use (Flask)
```bash
# Find process using port 5000
lsof -i :5000

# Kill the process
kill -9 <PID>

# Or use a different port
flask run --port 5001
```

---

## Adding New Shared Utilities

When you create a helper function that could be useful across projects:

1. Add it to `shared/utils/`
2. Create a descriptive module name (e.g., `gemini_helpers.py`)
3. Document the function with docstrings
4. Update this README with usage examples

Example:
```python
# shared/utils/gemini_helpers.py

def simple_generate(prompt, api_key=None):
    """
    Generate text using Gemini API with simplified interface.

    Args:
        prompt (str): The input prompt
        api_key (str, optional): API key (reads from env if not provided)

    Returns:
        str: Generated text response
    """
    # Implementation here
    pass
```

---

## Resources

- [Python dotenv Documentation](https://pypi.org/project/python-dotenv/)
- [Virtual Environments Guide](https://docs.python.org/3/tutorial/venv.html)
- [Conda User Guide](https://docs.conda.io/projects/conda/en/latest/user-guide/)
- [API Key Security Best Practices](https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_password)

---

**Keep your keys safe and your code shareable!** 🔐
