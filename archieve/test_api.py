import google.generativeai as genai
import os

# Securely loading the key we exported in the terminal
api_key = os.environ.get("GOOGLE_API_KEY")
genai.configure(api_key=api_key)

try:
    print("Connecting to Google AI...")
    model = genai.GenerativeModel('gemini-1.5-flash')
    response = model.generate_content("Say 'Connection Successful' if you can read this.")
    print(f"\nResponse from AI: {response.text}")
except Exception as e:
    print(f"\nIncident RCA: {e}")