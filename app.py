import os
import json
import streamlit as st
from groq import Groq
from dotenv import load_dotenv

# Configuration & Setup
load_dotenv()

def get_base64_image(image_path):
    import base64
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception:
        return ""

logo_path = r"C:\Users\Flipshope\Desktop\bot\images\logoHyyzo1.png"
logo_base64 = get_base64_image(logo_path)

# Custom High-Fidelity CSS
css = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600&display=swap');
    
    html, body, [class*="css"], .stApp {
        font-family: 'Inter', sans-serif !important;
    }
    
    /* Refined Visibility: Move the header buttons below the ribbon */
    header[data-testid="stHeader"] { 
        background: transparent !important;
        z-index: 1000001 !important;
        height: 60px !important;
        top: 60px !important; /* Move down below ribbon */
    }
    header[data-testid="stHeader"] div:first-child {
        background: transparent !important;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Background pattern like widget */
    .stApp { background-color: #f4f7f6; }
    
    /* Broadened Workspace - Overriding Streamlit Center */
    .stMainBlockContainer, 
    div[data-testid="stAppViewBlockContainer"],
    div.block-container {
        max-width: 1100px !important; 
        padding-top: 2rem !important;
        padding-bottom: 6rem !important;
        margin-left: auto !important;
        margin-right: auto !important;
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

    /* Clean Single-Box Chat Input */
    div[data-testid="stChatInput"] {
        border-radius: 26px !important;
        border: 1px solid #e5e5e5 !important;
        box-shadow: 0 4px 10px rgba(0,0,0,0.03) !important;
        padding: 5px !important;
        background-color: white !important;
        bottom: 0px !important; /* Absolute bottom */
    }
    /* Strip all internal borders/backgrounds from nested Streamlit divs */
    div[data-testid="stChatInput"] > div, 
    div[data-testid="stChatInputContainer"],
    div[data-testid="stChatInputContainer"] > div {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea {
        border: none !important;
        box-shadow: none !important;
        background-color: transparent !important;
        padding-left: 15px !important;
        outline: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"] textarea:focus {
        outline: none !important;
        box-shadow: none !important;
    }
    div[data-testid="stChatInput"]:focus-within {
        border-color: #e66912 !important;
        box-shadow: 0 4px 15px rgba(230,105,18,0.1) !important;
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
    /* Sidebar Styling - Precise ChatGPT Light Clone */
    [data-testid="stSidebar"] {
        background-color: #f9f9f9 !important;
        border-right: 1px solid rgba(0,0,0,0.1) !important;
        width: 260px !important;
        padding-top: 60px !important;
    }
    [data-testid="stSidebar"] > div:first-child { 
        width: 260px !important; 
        padding-top: 20px !important;
    }
    
    [data-testid="stSidebarNav"] { display: none; }
    
    /* Global Sidebar Button Reset */
    [data-testid="stSidebar"] .stButton button {
        background-color: transparent !important;
        color: #0d0d0d !important;
        border: none !important;
        box-shadow: none !important;
        border-radius: 8px !important;
        text-align: left !important;
        justify-content: flex-start !important;
        padding: 5px 12px !important;
        font-size: 14px !important;
        font-weight: 400 !important;
        line-height: 1.25rem !important;
        margin: 0 !important;
        width: 100% !important;
        transition: none !important;
    }
    [data-testid="stSidebar"] .stButton button:hover {
        background-color: rgba(0,0,0,0.05) !important;
    }
    
    /* Start New Conversation Button Style */
    .st-new-chat-btn button {
        margin-top: 10px !important;
        margin-bottom: 20px !important;
        font-weight: 500 !important;
        background-color: #f0f0f0 !important;
        border-radius: 12px !important;
        padding: 10px 15px !important;
        border: 1px solid rgba(0,0,0,0.05) !important;
    }
    .st-new-chat-btn button:hover {
        background-color: #e5e5e5 !important;
    }
    
    /* Active State - ChatGPT Capsule Look */
    div.active-chat div.stButton button {
        background-color: #ececec !important;
        border-radius: 20px !important;
        padding: 5px 12px !important;
    }

    /* Strict Sidebar Spacing Overrides */
    [data-testid="stSidebar"] div.stVerticalBlock { gap: 0px !important; }
    [data-testid="stSidebar"] div.stVerticalBlock > div {
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
        padding-top: 0px !important;
    }
    .recents-header {
        font-size: 11px;
        color: #676767;
        font-weight: 600;
        padding: 20px 14px 10px 14px;
        text-transform: uppercase;
    }    /* Sticky Top Ribbon Styling - Refined ChatGPT Layout */
    .top-ribbon {
        position: fixed;
        top: 0; 
        left: 0; 
        width: 100% !important;
        height: 60px;
        background-color: white;
        border-bottom: 1px solid rgba(0,0,0,0.05);
        display: flex; 
        align-items: center; 
        z-index: 1000000 !important;
        padding: 0; /* Remove global padding for precise alignment */
    }
    .ribbon-sidebar-area {
        width: 260px;
        padding: 0 15px;
        display: flex;
        align-items: center;
        gap: 15px;
        border-right: 1px solid transparent; /* Align with sidebar edge */
    }
    .ribbon-chat-area {
        flex-grow: 1;
        padding: 0 20px;
        display: flex;
        align-items: center;
        justify-content: space-between;
    }
    .hyzify-logo {
        width: 100px; /* Increased for wordmark maturity */
        height: 32px;
        background-image: url("data:image/png;base64,{logo_base64}");
        background-size: contain;
        background-repeat: no-repeat;
        background-position: left center;
        border-radius: 0; /* Wordmarks usually don't need rounded edges */
        display: flex; 
        align-items: center;
        justify-content: center;
        color: transparent;
    }
    .ribbon-text { 
        font-size: 16px; 
        font-weight: 500; 
        color: #0d0d0d; 
        display: flex; 
        align-items: center; 
        gap: 5px; 
        cursor: pointer;
    }
    .ribbon-icon {
        color: #676767;
        font-size: 18px;
        cursor: pointer;
    }
    /* Submit button circle */
    button[data-testid="stChatInputSubmit"] {
        background-color: #f26622 !important;
        color: white !important;
        border-radius: 50% !important;
        width: 32px !important;
        height: 32px !important;
        margin-right: 5px !important;
        transition: transform 0.2s ease !important;
    }
    button[data-testid="stChatInputSubmit"]:hover {
        background-color: #d1561b !important;
        transform: scale(1.05);
    }
</style>
"""
st.markdown(css.replace("{logo_base64}", logo_base64), unsafe_allow_html=True)

import time

HISTORY_INDEX_FILE = "chat_history.json"
CHATS_DIR = "chats"

def get_chat_filepath(chat_id):
    return os.path.join(CHATS_DIR, f"{chat_id}.json")

def load_index():
    if os.path.exists(HISTORY_INDEX_FILE):
        try:
            with open(HISTORY_INDEX_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, dict) and "conversations" in data:
                    # Check if messages are embedded and need to be moved to files
                    os.makedirs(CHATS_DIR, exist_ok=True)
                    for cid, cdata in data["conversations"].items():
                        if "messages" in cdata:
                            # Move messages to separate file if not already exists
                            mpath = get_chat_filepath(cid)
                            if not os.path.exists(mpath):
                                with open(mpath, "w", encoding="utf-8") as f2:
                                    json.dump(cdata["messages"], f2, indent=2)
                            # Remove messages from index to keep it lightweight
                            del cdata["messages"]
                    return data
                # Convert old list format to new index format
                if isinstance(data, list):
                    chat_id = f"chat_{int(time.time())}"
                    title = data[0]["content"][:30] if data and data[0]["role"] == "user" else "Migrated Chat"
                    new_index = {
                        "active_chat_id": chat_id,
                        "conversations": {
                            chat_id: {"title": title, "id": chat_id}
                        }
                    }
                    os.makedirs(CHATS_DIR, exist_ok=True)
                    with open(get_chat_filepath(chat_id), "w", encoding="utf-8") as f2:
                        json.dump(data, f2, indent=2)
                    return new_index
        except Exception as e:
            print(f"Error loading index: {e}")
    
    return {"active_chat_id": None, "conversations": {}}

def save_index(index_data):
    with open(HISTORY_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

def load_chat_messages(chat_id):
    path = get_chat_filepath(chat_id)
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading messages: {e}")
    return []

def save_chat_messages(chat_id, messages):
    if not os.path.exists(CHATS_DIR):
        os.makedirs(CHATS_DIR)
    
    # Simple deduplication and cleanup before saving
    seen_questions = set()
    deduped_messages = []
    skip_next_assistant = False
    
    for msg in messages:
        if msg["role"] == "user":
            q = msg["content"].strip().lower()
            if q in seen_questions:
                skip_next_assistant = True
            else:
                seen_questions.add(q)
                skip_next_assistant = False
                deduped_messages.append({"role": msg["role"], "content": msg["content"]})
        elif msg["role"] == "assistant":
            if not skip_next_assistant:
                deduped_messages.append({"role": msg["role"], "content": msg["content"]})
    
    # Prevent unlimited growth by capping the saved history (e.g. max 50 recent messages)
    MAX_HISTORY = 50
    if len(deduped_messages) > MAX_HISTORY:
        deduped_messages = deduped_messages[-MAX_HISTORY:]
        if deduped_messages and deduped_messages[0]["role"] == "assistant":
            deduped_messages = deduped_messages[1:]

    with open(get_chat_filepath(chat_id), "w", encoding="utf-8") as f:
        json.dump(deduped_messages, f, indent=2)

def sync_current_chat():
    if "chat_id" in st.session_state and st.session_state.chat_id:
        save_chat_messages(st.session_state.chat_id, st.session_state.messages)
        # Update title if it's still "New Chat" and we have a user message
        if st.session_state.index["conversations"][st.session_state.chat_id]["title"] == "New Chat":
            for msg in st.session_state.messages:
                if msg["role"] == "user":
                    st.session_state.index["conversations"][st.session_state.chat_id]["title"] = msg["content"][:30] + "..."
                    save_index(st.session_state.index)
                    break

# Helper to load KB
def load_kb():
    try:
        with open("Hyzify_Master_KB.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None

# Initialize session state for chat management
if "index" not in st.session_state:
    st.session_state.index = load_index()
    st.session_state.chat_id = st.session_state.index.get("active_chat_id")
    if st.session_state.chat_id:
        st.session_state.messages = load_chat_messages(st.session_state.chat_id)
    else:
        st.session_state.messages = []

def start_new_chat():
    new_id = f"chat_{int(time.time())}"
    st.session_state.chat_id = new_id
    st.session_state.messages = []
    st.session_state.index["conversations"][new_id] = {"title": "New Chat", "id": new_id}
    st.session_state.index["active_chat_id"] = new_id
    save_index(st.session_state.index)
    save_chat_messages(new_id, [])

def switch_chat(chat_id):
    st.session_state.chat_id = chat_id
    st.session_state.messages = load_chat_messages(chat_id)
    st.session_state.index["active_chat_id"] = chat_id
    save_index(st.session_state.index)

def delete_chat(chat_id):
    if chat_id in st.session_state.index["conversations"]:
        del st.session_state.index["conversations"][chat_id]
        path = get_chat_filepath(chat_id)
        if os.path.exists(path):
            os.remove(path)
        if st.session_state.chat_id == chat_id:
            st.session_state.chat_id = None
            st.session_state.messages = []
            st.session_state.index["active_chat_id"] = None
        save_index(st.session_state.index)

# Initialize Groq Client
api_key = os.getenv("GROQ_API_KEY")

# Sidebar UI
with st.sidebar:
    st.markdown('<div class="st-new-chat-btn">', unsafe_allow_html=True)
    if st.button("📝 Start a new conversation", help="Start a new conversation", use_container_width=True):
        start_new_chat()
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('<div class="recents-header">Recents</div>', unsafe_allow_html=True)
    
    conv_items = list(st.session_state.index["conversations"].items())
    # Filter out empty/unstructured chats before rendering to avoid gaps
    filtered_items = [
        (cid, conv) for cid, conv in reversed(conv_items) 
        if conv.get("title") and conv.get("title") != "New Chat"
    ]
    
    for chat_id, conv in filtered_items:
        is_active = (st.session_state.chat_id == chat_id)
        if is_active:
            st.markdown('<div class="active-chat">', unsafe_allow_html=True)
        
        title = conv.get('title', 'Untitled')
        if len(title) > 25:
            title = title[:22] + "..."
            
        if st.button(title, key=f"btn_{chat_id}", use_container_width=True):
            switch_chat(chat_id)
            st.rerun()
            
        if is_active:
            st.markdown('</div>', unsafe_allow_html=True)

# Sticky Top Ribbon
st.markdown("""
<div class="top-ribbon">
    <div class="ribbon-sidebar-area">
        <div class="hyzify-logo"></div>
    </div>
    <div class="ribbon-chat-area">
        <div class="ribbon-text">Chat with Hyzify <span style="font-size: 10px; opacity: 0.3;"></span></div>
        <div style="display: flex; gap: 20px; align-items: center;">
            <span style="font-size: 14px; cursor: pointer; color: #0d0d0d; font-weight: 500;">Share</span>
            <span class="ribbon-icon">⋮</span>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# Load all available API keys from environment
api_keys = []
for i in range(1, 10):
    k = os.getenv(f"GROQ_API_KEY_{i}")
    if k:
        api_keys.append(k)

# Fallback to standard key if no numbered keys exist
if not api_keys and api_key:
    api_keys.append(api_key)

if not api_keys:
    st.error("Missing GROQ_API_KEYs. Please add them to your .env file.")
    st.stop()

if "api_key_index" not in st.session_state:
    st.session_state.api_key_index = 0

kb_data = load_kb()
if not kb_data:
    st.error("Knowledge base file not found.")
    st.stop()

# Prepare System Instruction
kb_string = json.dumps(kb_data, indent=2)
system_prompt = f"""You are a friendly, concise support assistant for Hyzify. 
Your goal is to help team members with quick, ultra-short, human-friendly answers.

### KNOWLEDGE BASE:
{kb_string}

### YOUR PERSONALITY & SCOPE:
- You are an AI assistant EXCLUSIVELY for Hyzify. If a question is NOT Hyzify-related, politely decline (1 sentence).
- Be extremely concise. Avoid repeating facts or over-explaining.
- Use a warm, casual tone with 1-2 emojis per message. 👋
- For general facts, provide 1-2 sentence answers.
- For processes, use the EXACT steps from the KB without extra fluff.

### FEW-SHOT EXAMPLES (HOW TO FRAME):
User: "how to check my cashback"
✅ GOOD: "Checking your cashback is easy! 💰\n\nStep 1: Go to your Hyzify Dashboard.\n\nStep 2: Look for the 'Total earnings' section. 🚀"

User: "conversion of diamonds?"
✅ GOOD: "On Hyzify, 1 Diamond = ₹1! 💎 It's basically real money you can track easily. 👋"

User: "why do i need to verify my profile"
✅ GOOD: "Profile verification is mandatory for secure withdrawals and regulatory compliance. 🔒 It protects your account and ensures you can access your earnings! 🚀"

User: "Who is Elon Musk?"
✅ GOOD: "I'm the Hyzify AI! 🚀 I can only help with Hyzify-related questions like account settings or tools. 👋"

### INSTRUCTIONS:
1. BREVITY IS KEY: Keep responses short. Stop once the question is answered.
2. USE STEPS FOR PROCESSES ONLY: Use numbered steps (Step 1:) for instructions. For facts, use simple sentences.
3. EXACT STEPS ONLY: Output EXACT strings from KB arrays ('setup_steps', 'workflow', etc.). No embellishment.
4. STRICT NEWLINES: Double line break (`\n\n`) before EVERY step.
5. OVERRIDES & IMAGES: If a question matches `learned_responses`, use that info but keep it brief. ALWAYS include any Markdown images provided.
"""

def get_groq_client(current_api_key):
    return Groq(api_key=current_api_key)

# Display visible chat history with inline feedback
for i, message in enumerate(st.session_state.messages):
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Inline feedback — only for assistant messages
        if message["role"] == "assistant":
            feedback_key = f"feedback_{message.get('id', i)}"
            current_feedback = message.get("feedback")

            def handle_feedback(idx=i, key=feedback_key):
                fb_val = st.session_state[key]
                st.session_state.messages[idx]["feedback"] = fb_val
                sync_current_chat()

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
    # If no active chat, start one automatically
    if not st.session_state.chat_id:
        start_new_chat()

    # Add user message
    st.session_state.messages.append({
        "role": "user",
        "content": prompt,
        "id": len(st.session_state.messages),
        "feedback": None
    })
    sync_current_chat()

    with st.chat_message("user"):
        st.markdown(prompt)

    # Build message history for Groq (all messages including hidden ones)
    groq_messages = [{"role": "system", "content": system_prompt}]
    for m in st.session_state.messages[:-1]:
        groq_messages.append({"role": m["role"], "content": m["content"]})
    groq_messages.append({"role": "user", "content": prompt})

    # Rotate API keys round-robin
    current_key_val = api_keys[st.session_state.api_key_index]
    client = get_groq_client(current_key_val)
    st.session_state.api_key_index = (st.session_state.api_key_index + 1) % len(api_keys)

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
            sync_current_chat()
            st.rerun()

        except Exception as e:
            st.error(f"Error: {e}")


        except Exception as e:
            st.error(f"Error: {e}")

