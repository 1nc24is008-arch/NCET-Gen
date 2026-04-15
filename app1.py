import streamlit as st
from groq import Groq
import time

# ---------------- PAGE CONFIG ----------------
st.set_page_config(page_title="Genz_AI", layout="wide")

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.title("🤖 Genz_AI")
    
    if st.button("➕ New Chat"):
        st.session_state.messages = []

    st.markdown("---")
    st.write("Simple ChatGPT Clone using Groq")

# ---------------- INIT ----------------
client = Groq(api_key=st.secrets["app2"])

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------- TITLE ----------------
st.title("💬 ChatGPT Clone")

# ---------------- DISPLAY CHAT ----------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ---------------- USER INPUT ----------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Save user message
    st.session_state.messages.append({"role": "user", "content": user_input})

    # Display user message
    with st.chat_message("user"):
        st.markdown(user_input)

    # Generate response
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        full_response = ""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=st.session_state.messages,
                stream=True
            )

            for chunk in response:
                content = chunk.choices[0].delta.content or ""
                full_response += content
                message_placeholder.markdown(full_response + "▌")
                time.sleep(0.01)

            message_placeholder.markdown(full_response)

        except Exception as e:
            full_response = "⚠️ Error generating response"
            st.error(e)

    # Save assistant message
    st.session_state.messages.append(
        {"role": "assistant", "content": full_response}
    )
