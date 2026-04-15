import streamlit as st
from groq import Groq
import time

# Page Config
st.set_page_config(page_title="Genz_AI", layout="wide")

# 🎨 Dark + Chat UI Styling
st.markdown("""
<style>
.stApp {
    background-color: black;
    color: white;
}

header, footer {
    visibility: hidden;
}

/* Chat bubbles */
.user-msg {
    background-color: #1a1a1a;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    text-align: right;
}

.bot-msg {
    background-color: #111;
    padding: 12px;
    border-radius: 10px;
    margin-bottom: 10px;
    text-align: left;
    border-left: 3px solid red;
}

/* Inputs */
.stTextInput>div>div>input {
    background-color: #111;
    color: white;
    border-radius: 10px;
}

/* Button */
.stButton>button {
    background-color: red;
    color: white;
    border-radius: 10px;
    width: 100%;
    box-shadow: 0 0 10px red;
}
</style>
""", unsafe_allow_html=True)

# Title
st.title("⚡ Genz_AI")

# Initialize client
client = Groq(api_key=st.secrets["First_project"])

# Session state for chat
if "chat" not in st.session_state:
    st.session_state.chat = []

# Mode selection
mode = st.selectbox("Select Content Type", ["Marketing", "Blog", "Instagram Caption"])

# Input
user_input = st.text_input("Enter your idea...")

# Generate button
if st.button("Generate"):
    if user_input:
        
        # Prompt based on mode
        if mode == "Marketing":
            prompt = f"Write marketing content for: {user_input}"
        elif mode == "Blog":
            prompt = f"Write a detailed blog on: {user_input}"
        else:
            prompt = f"Write an engaging Instagram caption for: {user_input}"

        # Save user message
        st.session_state.chat.append(("user", user_input))

        with st.spinner("Thinking..."):
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}]
            )

            reply = response.choices[0].message.content

            # Typing effect
            typed = ""
            placeholder = st.empty()
            for char in reply:
                typed += char
                placeholder.markdown(f"<div class='bot-msg'>{typed}</div>", unsafe_allow_html=True)
                time.sleep(0.01)

            # Save bot reply
            st.session_state.chat.append(("bot", reply))

    else:
        st.warning("Enter something first!")

# Display chat history
for role, msg in st.session_state.chat:
    if role == "user":
        st.markdown(f"<div class='user-msg'>{msg}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='bot-msg'>{msg}</div>", unsafe_allow_html=True)
