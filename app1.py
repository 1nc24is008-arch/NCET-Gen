import streamlit as st
from groq import Groq
import time
import uuid
import json
import os

# ---------------- FILE ----------------
CHAT_FILE = "chats.json"

def load_chats():
    if os.path.exists(CHAT_FILE):
        with open(CHAT_FILE, "r") as f:
            return json.load(f)
    return {}

def save_chats(chats):
    with open(CHAT_FILE, "w") as f:
        json.dump(chats, f)

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Genz_AI", layout="wide")

# ---------------- YOUR CSS (IMPROVED) ----------------
/* SIDEBAR BASE */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #111827, #0B0F19);
    padding: 20px 12px;
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* APP TITLE */
[data-testid="stSidebar"] h1 {
    font-size: 20px;
    font-weight: 600;
    color: #F9FAFB;
    margin-bottom: 20px;
}

/* SECTION TITLE */
[data-testid="stSidebar"] h3 {
    font-size: 13px;
    color: #9CA3AF;
    margin-top: 20px;
    margin-bottom: 8px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
}

/* BUTTON BASE */
.stButton > button {
    width: 100%;
    border-radius: 10px;
    background: #1F2937;
    color: #E5E7EB;
    border: 1px solid transparent;
    padding: 10px 12px;
    text-align: left;
    font-size: 14px;
    transition: all 0.25s ease;
}

/* BUTTON HOVER */
.stButton > button:hover {
    background: #374151;
    border: 1px solid #4B5563;
    transform: translateX(2px);
}

/* ACTIVE CHAT STYLE */
.stButton > button:focus {
    background: #2563EB !important;
    color: white !important;
    border: none;
}

/* NEW CHAT BUTTON SPECIAL */
.stButton:first-child > button {
    background: linear-gradient(135deg, #2563EB, #1D4ED8);
    color: white;
    font-weight: 500;
    text-align: center;
}

.stButton:first-child > button:hover {
    background: linear-gradient(135deg, #1D4ED8, #1E40AF);
}

/* CHAT ROW (FIX ICON ALIGNMENT) */
[data-testid="stSidebar"] .stColumns {
    align-items: center;
}

/* ICON BUTTONS (EDIT / DELETE) */
[data-testid="stSidebar"] button[kind="secondary"] {
    padding: 6px !important;
    border-radius: 8px !important;
    background: transparent !important;
}

[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: #374151 !important;
}

/* SCROLLBAR */
[data-testid="stSidebar"] ::-webkit-scrollbar {
    width: 5px;
}

[data-testid="stSidebar"] ::-webkit-scrollbar-thumb {
    background: #4B5563;
    border-radius: 10px;
}
# ---------------- INIT ----------------
client = Groq(api_key=st.secrets["app2"])

if "chats" not in st.session_state:
    st.session_state.chats = load_chats()

if "current_chat" not in st.session_state:
    if st.session_state.chats:
        st.session_state.current_chat = list(st.session_state.chats.keys())[0]
    else:
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = chat_id
        save_chats(st.session_state.chats)

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🤖 Genz_AI")

    if st.button("➕ New Chat", use_container_width=True):
        chat_id = str(uuid.uuid4())
        st.session_state.chats[chat_id] = {"name": "New Chat", "messages": []}
        st.session_state.current_chat = chat_id
        save_chats(st.session_state.chats)
        st.rerun()

    st.markdown("---")
    st.markdown("### 💬 Your Chats")

    for chat_id, chat_data in list(st.session_state.chats.items()):
        col1, col2, col3 = st.columns([6,1,1])

        # Select Chat
        with col1:
            if st.button(chat_data["name"], key=f"chat_{chat_id}"):
                st.session_state.current_chat = chat_id
                st.rerun()

        # Rename
        with col2:
            if st.button("✏️", key=f"rename_{chat_id}"):
                new_name = st.text_input("Rename", key=f"input_{chat_id}")
                if new_name:
                    st.session_state.chats[chat_id]["name"] = new_name
                    save_chats(st.session_state.chats)
                    st.rerun()

        # Delete
        with col3:
            if st.button("❌", key=f"del_{chat_id}"):
                del st.session_state.chats[chat_id]
                if not st.session_state.chats:
                    new_chat = str(uuid.uuid4())
                    st.session_state.chats[new_chat] = {"name": "New Chat", "messages": []}
                    st.session_state.current_chat = new_chat
                else:
                    st.session_state.current_chat = list(st.session_state.chats.keys())[0]
                save_chats(st.session_state.chats)
                st.rerun()

# ---------------- MAIN ----------------
current_chat = st.session_state.current_chat
chat_data = st.session_state.chats[current_chat]
messages = chat_data["messages"]

st.markdown(f"<div class='chat-title'>💬 {chat_data['name']}</div>", unsafe_allow_html=True)

# ---------------- DISPLAY ----------------
for msg in messages:
    avatar = "🧑" if msg["role"] == "user" else "🤖"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# ---------------- INPUT ----------------
user_input = st.chat_input("Type your message...")

if user_input:
    if chat_data["name"] == "New Chat":
        chat_data["name"] = user_input[:30]

    messages.append({"role": "user", "content": user_input})

    with st.chat_message("user", avatar="🧑"):
        st.markdown(user_input)

    with st.chat_message("assistant", avatar="🤖"):
        placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=messages,
                stream=True
            )

            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                placeholder.markdown(full_response + "▌")
                time.sleep(0.01)

            placeholder.markdown(full_response)

        except Exception as e:
            full_response = "⚠️ Error generating response"
            st.error(e)

    messages.append({"role": "assistant", "content": full_response})

    st.session_state.chats[current_chat]["messages"] = messages
    save_chats(st.session_state.chats)
