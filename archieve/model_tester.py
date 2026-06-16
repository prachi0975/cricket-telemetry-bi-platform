import os
import sys
from google import genai

def find_working_model():
    print("Initiating Diagnostic RCA: Testing available Gemini Models...\n")
    
    api_key = os.environ.get("GOOGLE_API_KEY")
    if not api_key:
        print("Incident: GOOGLE_API_KEY not found.")
        sys.exit(1)
        
    client = genai.Client(api_key=api_key)
    
    # List of stable models to test
    models_to_test = [
        'gemini-1.5-flash-8b',   # High free quota, fast
        'gemini-1.5-pro',        # Heavy reasoning
        'gemini-1.0-pro',        # Legacy stable
        'gemini-1.5-flash-latest' # Rolling latest
    ]
    
    working_model = None
    
    for model_name in models_to_test:
        try:
            print(f"Pinging {model_name}...")
            response = client.models.generate_content(
                model=model_name,
                contents="Reply with 'OK'"
            )
            print(f"✅ SUCCESS: '{model_name}' is fully functional on your account!\n")
            working_model = model_name
            break # Stop at the first working model
        except Exception as e:
            # Extracting just the error code/message for cleaner logs
            error_msg = str(e).split('message')[0][:100] + "..." 
            print(f"❌ FAILED: '{model_name}' -> {error_msg}\n")
            
    if working_model:
        print(f"--- ACTION REQUIRED ---")
        print(f"Open 'ai_agent.py' and change the model name to: {working_model}")
    else:
        print("All tested models failed. We might need to check your Google Cloud Billing settings.")

if __name__ == "__main__":
    find_working_model()