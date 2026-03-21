import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(page_title="Hyzify AI Assistant", page_icon="🚀", layout="centered")

# Custom CSS for Hyzify branding
st.markdown("""
<style>
    /* Reset Streamlit defaults */
    header[data-testid="stHeader"] { display: none; }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Background pattern like widget */
    .stApp { background-color: #f4f7f6; }
    
    /* Container max-width to simulate a mobile widget */
    div.block-container {
        max-width: 480px;
        padding-top: 1rem;
        padding-bottom: 5rem;
    }

    /* Custom Header implemented via markdown */
    .widget-header {
        background: #e66912;
        color: white;
        padding: 20px;
        border-radius: 20px 20px 0 0;
        display: flex;
        align-items: center;
        gap: 15px;
        margin-bottom: 20px;
        box-shadow: 0 4px 10px rgba(230,105,18,0.2);
        margin-top: -15px;
    }
    .widget-header-text { flex-grow: 1; }
    .widget-header-text h3 {
        margin: 0; font-size: 1.1rem; font-weight: 600; color: white !important;
        padding-bottom: 5px;
    }
    .widget-header-text p {
        margin: 0; font-size: 0.85rem; opacity: 0.9; display: flex; align-items: center; gap: 6px;
    }
    .status-dot {
        width: 8px; height: 8px; background-color: #4CAF50; border-radius: 50%; display: inline-block;
    }

    /* Assistant Message Bubble */
    div[data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) {
        background: transparent;
    }
    div[data-testid="stChatMessage"]:not(:has([data-testid="chatAvatarIcon-user"])) div[data-testid="stChatMessageContent"] {
        background-color: white;
        color: #333;
        border-radius: 20px 20px 20px 5px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.04);
        border: 1px solid #eaeaea;
    }

    /* User Message Bubble */
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
        flex-direction: row-reverse;
        background: transparent;
    }
    div[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) div[data-testid="stChatMessageContent"] {
        background-color: #e66912;
        color: white;
        border-radius: 20px 20px 5px 20px;
        padding: 15px;
        box-shadow: 0 2px 10px rgba(230,105,18,0.2);
    }
    /* Hide Avatars to match sleek UI */
    div[data-testid="chatAvatarIcon-user"], div[data-testid="chatAvatarIcon-assistant"] {
        display: none !important;
    }

    /* Input Box */
    div[data-testid="stChatInput"] {
        border-radius: 30px !important;
        border: 1px solid #ddd;
        box-shadow: 0 -5px 15px rgba(0,0,0,0.03);
        padding: 5px 10px;
        background-color: white;
    }
    div[data-testid="stChatInputFocus"] {
        border-color: #e66912 !important;
    }
    
    /* Send Button */
    button[data-testid="stChatInputSubmitButton"] {
        background-color: #e66912 !important;
        border-radius: 50% !important;
        height: 38px !important; width: 38px !important;
        display: flex; justify-content: center; align-items: center; padding: 0 !important;
    }
    button[data-testid="stChatInputSubmitButton"] svg { fill: white !important; }

    /* Hide redundant elements */
    .stFeedback { padding-top: 5px; opacity: 0.8; }
</style>
""", unsafe_allow_html=True)

def load_kb():
    try:
        with open("Hyzify_Master_KB.json", "r", encoding="utf-8") as f:
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

# Custom HTML Header instead of standard title
st.markdown("""
<div class="widget-header">
    <div style="font-size: 35px; line-height: 1; padding: 5px; background: rgba(255,255,255,0.2); border-radius: 50%;">🚀</div>
    <div class="widget-header-text">
        <h3>Chat with Hyzify</h3>
        <p><span class="status-dot"></span> We're online</p>
    </div>
    <div style="font-size: 24px; cursor: pointer; opacity: 0.8;">⋮</div>
    <div style="font-size: 22px; cursor: pointer; opacity: 0.8;">⌄</div>
</div>
""", unsafe_allow_html=True)

if not api_key:
    st.error("Missing GROQ_API_KEY. Please add it to your .env file. Get a free key at https://console.groq.com/")
    st.stop()

kb_data = load_kb()
if not kb_data:
    st.error("Knowledge base file not found.")
    st.stop()

# Prepare System Instruction
kb_string = json.dumps(kb_data, indent=2)
system_prompt = f"""You are a friendly, on-point support assistant for Hyzify. 
Your goal is to help team members with quick, human-friendly answers.

### KNOWLEDGE BASE:
{kb_string}

### YOUR PERSONALITY & SCOPE:
- You are an AI assistant EXCLUSIVELY for Hyzify. If a user asks a question that is NOT related to Hyzify, you MUST politely decline to answer and state that you can only help with Hyzify-related queries. Do NOT answer general knowledge questions.
- You are a helpful teammate, not a database retriever.
- NEVER copy-paste raw data. Instead, READ and NARRATE it naturally.
- Use a warm, casual tone with emojis. 👋

### FEW-SHOT EXAMPLES (HOW TO FRAME):
User: "how to check my cashback"
❌ BAD: "Step 1: Go to dashboard. Step 2: Look for earnings."
✅ GOOD: "Checking your cashback is easy! 💰\n\nStep 1: Go to your Hyzify Dashboard.\n\nStep 2: Look for the 'Total earnings' section to see your tracked cashback. 🚀"

User: "conversion of diamonds?"
❌ BAD (Using steps for facts): "Step 1: Diamonds are real money. Step 2: 1 Diamond = 1 INR."
✅ GOOD (Human): "On Hyzify, Diamonds are basically real money! 💎 1 Diamond equals ₹1, so you can track your earnings easily. 👋"

User: "Who is Elon Musk?"
❌ BAD: "Elon Musk is the CEO of Tesla and SpaceX."
✅ GOOD: "I am the Hyzify AI Assistant! 🚀 I can only answer questions related to your Hyzify account, deals, or tools. Let me know if you need help with your Dashboard or Converter Bots! 👋"

### INSTRUCTIONS:
1. USE STEPS FOR PROCESSES ONLY: If the user asks how to do something (a process or instruction), use a numbered format (Step 1:, Step 2:). If it's just a general question or fact, just answer normally without steps.
2. STRICT NEWLINES: When you do write steps, you MUST put a double line break (`\n\n`) before EVERY single step so they appear on separate lines. NEVER group steps on the same line.
3. CRITICAL - OVERRIDES & IMAGES: If the user's question matches a question in `learned_responses`, use that factual info but still frame it in YOUR own words. HOWEVER, if the `correct_answer` contains an image in Markdown format, you MUST include that EXACT markdown code in your final response somewhere. Never remove images.
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
                            with open("Hyzify_Master_KB.json", "w", encoding="utf-8") as f:
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

