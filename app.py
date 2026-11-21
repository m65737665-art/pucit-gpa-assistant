import streamlit as st
from agent import run_agent


# -----------------------------
# Page configuration
# -----------------------------
st.set_page_config(
    page_title="PUCIT GPA Assistant",
    layout="centered"
)


# -----------------------------
# Initialize conversation history
# -----------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []


# -----------------------------
# Sidebar
# -----------------------------
with st.sidebar:
    if st.button("＋ New Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()


# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
    <div style="text-align: center; margin-top: 20px;">
        <h1>PUCIT GPA Assistant</h1>
        <p style="font-size: 17px; color: #666;">
            Conversational GPA & CGPA Assistant
        </p>
    </div>
    """,
    unsafe_allow_html=True
)


# -----------------------------
# Display previous messages
# -----------------------------
for message in st.session_state.messages:

    if message.type == "human":
        with st.chat_message("user"):
            st.write(message.content)

    elif message.type == "ai" and message.text:
        with st.chat_message("assistant"):
            st.write(message.text)


# -----------------------------
# User input
# -----------------------------
user_input = st.chat_input(
    "Ask me about your GPA or CGPA..."
)


# -----------------------------
# Process user message
# -----------------------------
if user_input:

    # Display user's message immediately
    with st.chat_message("user"):
        st.write(user_input)

    # Run the agent and maintain conversation history
    st.session_state.messages = run_agent(
        user_input,
        st.session_state.messages
    )

    # Get the final AI response
    final_response = st.session_state.messages[-1].text

    # Display the agent's response
    with st.chat_message("assistant"):
        st.write(final_response)