import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Hyyzo AI Assistant", page_icon="🚀", layout="centered")

# Custom CSS for Hyyzo branding
st.markdown("""
<style>
    .stApp { background-color: #f8f9fa; }
    .stChatMessage { border-radius: 15px; }
    h1 { color: #6c5ce7; }
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
                history = json.load(f)
                for msg in history:
                    msg["hidden"] = True
                return history
    except Exception:
        pass
    return []

def save_chat_history(messages):
    try:
        clean_messages = [{"role": m["role"], "content": m["content"]} for m in messages]
        with open("chat_history.json", "w", encoding="utf-8") as f:
            json.dump(clean_messages, f, indent=2)
    except Exception as e:
        print(f"Error saving history: {e}")

# Initialize session state for chat history (hidden past + visible current)
if "messages" not in st.session_state:
    st.session_state.messages = load_chat_history()

def sync_history():
    save_chat_history(st.session_state.messages)

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")

st.title("🚀 Hyyzo AI Support")
st.caption("On-point, friendly help for the Hyyzo community.")

if not api_key:
    st.error("Missing GROQ_API_KEY. Please add it to your .env file. Get a free key at https://console.groq.com/")
    st.stop()

kb_data = load_kb()
if not kb_data:
    st.error("Knowledge base file not found.")
    st.stop()

# Prepare System Instruction
kb_string = json.dumps(kb_data, indent=2)
system_prompt = f"""You are a friendly, on-point support assistant for Hyyzo. 
Your goal is to help team members with quick, human-friendly answers.

### KNOWLEDGE BASE:
{kb_string}

### YOUR PERSONALITY:
- You are a helpful teammate, not a database retriever.
- NEVER copy-paste raw data. Instead, READ and NARRATE it naturally.
- Avoid structured lists/bullets for simple questions. Use flowing sentences.
- Use a warm, casual tone with emojis. 👋

### FEW-SHOT EXAMPLES (HOW TO NARRATE):
User: "How to change number?"
❌ BAD (Robotic): "Email support@hyyzo.com with old and new number."
✅ GOOD (Human): "Hey! It's easy to change your number. Just drop an email to support@hyyzo.com from your registered ID, and make sure to include both your old and new numbers. 🚀"

User: "conversion of diamonds?"
❌ BAD (Robotic): "1 Diamond = 1 INR."
✅ GOOD (Human): "On Hyyzo, Diamonds are basically real money! 💎 1 Diamond equals ₹1, so you can track your earnings easily. 👋"

### INSTRUCTIONS:
1. NARRATE: Always frame your answer as a friendly chat response.
2. CRITICAL - OVERRIDES & IMAGES: If the user's question matches a question in `learned_responses`, use that factual info but still frame it in YOUR own words. HOWEVER, if the `correct_answer` contains an image in Markdown format (like `![alt text](url)`), you MUST include that EXACT markdown code in your final response somewhere. Never remove images.
3. BE CONCISE: Stick to one short, punchy paragraph.
"""

@st.cache_resource
def get_groq_client():
    return Groq(api_key=api_key)

client = get_groq_client()

# Display visible chat history with inline feedback
for i, message in enumerate(st.session_state.messages):
    if not message.get("hidden", False):
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

        # Inline feedback — only for assistant messages
        if message["role"] == "assistant":
            feedback_key = f"feedback_{message.get('id', i)}"
            current_feedback = message.get("feedback")

            def handle_feedback(idx=i, key=feedback_key):
                fb_val = st.session_state[key]
                st.session_state.messages[idx]["feedback"] = fb_val

            if current_feedback is None:
                st.feedback("thumbs", key=feedback_key, on_change=handle_feedback)
            elif current_feedback == 1:
                st.success("👍 Thanks for the positive feedback!")
            elif current_feedback == 0:
                st.warning("👎 Thanks for the feedback. How should I have answered?")
                with st.form(key=f"edit_form_{message.get('id', i)}"):
                    question = ""
                    if i > 0 and st.session_state.messages[i-1]["role"] == "user":
                        question = st.session_state.messages[i-1]["content"]
                    st.write(f"**Question:** {question}")
                    corrected_answer = st.text_area("Provide the Correct Answer:", value=message["content"])
                    if st.form_submit_button("💾 Save to Knowledge Base"):
                        kb_data = load_kb()
                        if kb_data:
                            if "learned_responses" not in kb_data:
                                kb_data["learned_responses"] = []
                            kb_data["learned_responses"].append({
                                "question": question,
                                "correct_answer": corrected_answer,
                                "added_by_team": True
                            })
                            with open("Hyyzo_Master_KB.json", "w", encoding="utf-8") as f:
                                json.dump(kb_data, f, indent=2)
                            st.success("✅ Saved! The bot will use this answer next time.")
                            st.session_state.messages[i]["feedback"] = 2
                            st.rerun()

# User Input
if prompt := st.chat_input("How can I help you today?"):
    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "id": len(st.session_state.messages),
        "feedback": None
    })
    sync_history()

    with st.chat_message("user"):
        st.markdown(prompt)

    # Build message history for Groq (all messages including hidden ones)
    groq_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[:-1]:
        groq_messages.append({"role": m["role"], "content": m["content"]})
    groq_messages.append({"role": "user", "content": prompt})

    # Generate response with streaming
    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        full_response = ""

        try:
            stream = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=groq_messages,
                stream=True,
                temperature=0.8,
                max_tokens=1024,
            )

            for chunk in stream:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response += delta
                    response_placeholder.markdown(full_response + "▌")

            response_placeholder.markdown(full_response)

            # Save assistant response
            msg_id = len(st.session_state.messages)
            st.session_state.messages.append({
                "role": "assistant",
                "content": full_response,
                "id": msg_id,
                "feedback": None
            })
            sync_history()
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")

