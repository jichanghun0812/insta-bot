import os
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=api_key)

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Hello, this is a test. Reply with 'OK' if you work.")
    print(f"Response: {response.text}")
except Exception as e:
    print(f"Error: {e}")
