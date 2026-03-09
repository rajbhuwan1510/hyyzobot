import os
import json
import streamlit as st
from google import genai
from google.genai import types
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Hyyzo AI Assistant", page_icon="🚀", layout="centered")

# Custom CSS for Hyyzo branding (Purple/Flashy theme)
st.markdown("""
<style>
    .stApp {
        background-color: #f8f9fa;
    }
    .stChatMessage {
        border-radius: 15px;
    }
    h1 {
        color: #6c5ce7;
    }
</style>
""", unsafe_allow_html=True)

def load_kb():
    try:
        with open("Hyyzo_Master_KB.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

def load_chat_history():
    try:
        if os.path.exists("chat_history.json"):
            with open("chat_history.json", "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception:
        pass
    return []

def save_chat_history(messages):
    try:
        # We don't need to save the feedback UI state to permanent history
        clean_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(clean_messages, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

# Save history callback wrapper
def sync_history():
    save_chat_history(st.session_state.messages)

# Initialize Gemini Client
api_key = os.getenv("GEMINI_API_KEY")

st.title("🚀 Hyyzo AI Support")
st.caption("On-point, friendly help for the Hyyzo community.")

if not api_key:
    st.error("Missing GEMINI_API_KEY. Please add it to your .env file.")
    st.stop()

kb_data = load_kb()
if not kb_data:
    st.error("Knowledge base file not found.")
    st.stop()

# Prepare System Instruction (Humanized & Concise)
kb_string = json.dumps(kb_data, indent=2)
system_instruction = f"""
You are a friendly, on-point support assistant for Hyyzo. 
Your goal is to help users and team members with quick, human-like answers based on the Knowledge Base.

### KNOWLEDGE BASE:
{kb_string}

### INSTRUCTIONS:
1. BE CONCISE: Use short sentences. One paragraph max unless steps are needed.
2. BE HUMAN: Use friendly emojis like 👋, 💎, 🚀. Speak like a teammate.
3. PRIORITIZE KB: Use the official data provided.
4. SPEED: Get to the point quickly.
5. HONESTY: If it's not in the KB, give a helpful guess but clarify it's not official info.
"""

@st.cache_resource
def get_chat_client():
    client = genai.Client(api_key=api_key)
    return client

client = get_chat_client()

# Reconstruct chat session from session state
# Note: In Streamlit, we often just pass the whole history to the model
# but Gemini's start_chat manages history itself. 
# For UI consistency, we display session_state.messages.

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Clear previous thought and display user message
    st.session_state.messages.append({"role": "user", "content": prompt, "id": len(st.session_state.messages), "feedback": None})
    sync_history()
    
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""
        
        try:
            # We use a fresh chat session for each prompt or maintain one depending on architecture
            # To keep it simple and reliable with Streamlit's rerun, we can use the messages list.
            chat = client.chats.create(
                model="gemini-flash-latest",
                config=types.GenerateContentConfig(
                    system_instruction=system_instruction
                ),
                history=[
                    types.Content(
                        role="model" if m["role"] == "assistant" else "user",
                        parts=[types.Part(text=m["content"])]
                    ) 
                    for m in st.session_state.messages[:-1]
                ]
            )
            
            # --- SPEED UP: Use Streaming ---
            response_stream = chat.send_message_stream(prompt)
            
            for chunk in response_stream:
                if chunk.text:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
            
            response_placeholder.markdown(full_response)
            
            # Save assistant message with unique ID for feedback tracking
            msg_id = len(st.session_state.messages)
            st.session_state.messages.append({
                "role": "assistant", 
                "content": full_response,
                "id": msg_id,
                "feedback": None
            })
            sync_history()

            # Force a rerun to show feedback buttons immediately
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

# Process feedback and display "Edit" options
for i, msg in enumerate(st.session_state.messages):
    if msg["role"] == "assistant":
        # Feedback mechanism
        feedback_key = f"feedback_{msg.get('id', i)}"
        
        # Determine current feedback state
        current_feedback = msg.get("feedback")
        
        def handle_feedback(idx=i, key=feedback_key):
            # Streamlit feedback returns 1 for thumbs up, 0 for thumbs down
            fb_val = st.session_state[key]
            st.session_state.messages[idx]["feedback"] = fb_val

        if current_feedback is None:
            st.feedback("thumbs", key=feedback_key, on_change=handle_feedback)
        elif current_feedback == 1:
            st.success("👍 Thanks for the positive feedback!")
        elif current_feedback == 0:
            st.warning("👎 Thanks for the feedback. How should I have answered?")
            
            # --- Edit & Learn Feature ---
            with st.form(key=f"edit_form_{msg.get('id', i)}"):
                # Find the user question that prompted this answer
                question = ""
                if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                    question = st.session_state.messages[i-1]["content"]
                
                st.write(f"**Question:** {question}")
                corrected_answer = st.text_area("Provide the Correct Answer to save to Knowledge Base:", value=msg["content"])
                
                if st.form_submit_button("Save to Knowledge Base"):
                    # Append new knowledge to JSON
                    kb_data = load_kb()
                    if kb_data:
                        if "learned_responses" not in kb_data:
                            kb_data["learned_responses"] = []
                        
                        kb_data["learned_responses"].append({
                            "question": question,
                            "correct_answer": corrected_answer,
                            "added_by_team": True
                        })
                        
                        # Save back to file
                        with open("Hyyzo_Master_KB.json", "w", encoding="utf-8") as f:
                            json.dump(kb_data, f, indent=2)
                        
                        st.success("✅ New knowledge saved successfully! The bot will use this answer next time.")
                        st.session_state.messages[i]["feedback"] = 2 # Mark as resolved to close form
                        st.rerun()
