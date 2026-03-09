import os
import json
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def load_knowledge_base(file_path):
    """Loads the knowledge base from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading knowledge base: {e}")
        return None

def main():
    kb_path = "Hyyzo_Master_KB.json"
    kb_data = load_knowledge_base(kb_path)
    
    if not kb_data:
        print("Failed to start bot: Knowledge base not found.")
        return

    # Check for Gemini API key
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or api_key == "your_gemini_api_key_here":
        print("\n[!] Error: GEMINI_API_KEY is not set.")
        print("Please follow these steps:")
        print("1. Get a FREE key from: https://aistudio.google.com/app/apikey")
        print("2. Create a '.env' file in this directory.")
        print("3. Add 'GEMINI_API_KEY=your_key_here' to the file.")
        print("4. Restart the bot.")
        return

    # Initialize Gemini client
    client = genai.Client(api_key=api_key)
    
    # Format KB for system prompt
    kb_string = json.dumps(kb_data, indent=2)
    
    system_instruction = f"""
You are a friendly, on-point support assistant for Hyyzo. 
Your goal is to help users and team members with quick, human-like answers based on the Knowledge Base.

### KNOWLEDGE BASE:
{kb_string}

### INSTRUCTIONS:
1. BE CONCISE: Don't write paragraphs if a sentence works. Use bullet points for steps.
2. BE HUMAN: Speak like a helpful teammate, not a manual. Use a warm but professional tone.
3. PRIORITIZE KB: Use the official data above first.
4. HONEST FALLBACK: If it's not in the KB, give a smart guess but mention it's not official.
5. REMEMBER: Keep track of the chat flow.
"""

    # Start chat with config
    chat = client.chats.create(
        model="gemini-flash-latest",
        config=types.GenerateContentConfig(
            system_instruction=system_instruction
        )
    )

    print("--- Hyyzo (Gemini Free Tier) Chatbot Started ---")
    print("Type 'exit' or 'quit' to stop.")

    while True:
        try:
            user_input = input("\nYou: ")
            
            if user_input.lower() in ['exit', 'quit']:
                break

            response = chat.send_message(user_input)
            print(f"\nBot: {response.text}")

        except Exception as e:
            print(f"\nError: {e}")
            if "api_key" in str(e).lower() or "invalid" in str(e).lower():
                print("Tip: Ensure your GEMINI_API_KEY is correct in your .env file.")

if __name__ == "__main__":
    main()
