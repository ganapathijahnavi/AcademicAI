import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load .env file
load_dotenv()

# Get API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    raise ValueError("GEMINI_API_KEY not set in .env file")

# Configure Gemini
genai.configure(api_key=api_key)

# Initialize model
model = genai.GenerativeModel("gemini-1.5-flash")

# Test prompt
prompt = "Hello Gemini! Can you explain Computer Networks in simple terms?"

response = model.generate_content(prompt)

print("✅ Gemini Response:\n")
print(response.text)
