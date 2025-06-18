import os
import streamlit as st
from together import Together

# --- 1️⃣ Load API key & instantiate Together client ---
api_key = st.secrets.get("together_ai_api_key") or os.getenv("TOGETHER_API_KEY")
if not api_key:
    st.error(
        "🔑 Missing Together AI API key.\n"
        "Set `together_ai_api_key` in `.streamlit/secrets.toml` or `TOGETHER_API_KEY` env var."
    )
    st.stop()
# Ensure the Together library picks up the key
os.environ["TOGETHER_API_KEY"] = api_key
client = Together(api_key=api_key)

# --- 2️⃣ Session state for chat history ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- 3️⃣ Page setup ---
st.set_page_config(page_title="Fast LLM Chat", page_icon="🤖")
st.title("🤖 Fast Streamlit LLM Chat with Streaming")

# --- 4️⃣ Supported Model ---
MODEL_NAME = "deepseek-ai/DeepSeek-V3"  # update when additional models are available

# --- 5️⃣ Streaming response function ---
def stream_response(prompt: str) -> str:
    """Stream tokens in real time from Together AI."""
    try:
        stream = client.chat.completions.create(
            model=MODEL_NAME,
            messages=[{"role": "user", "content": prompt}],
            stream=True,
        )
    except Exception as e:
        st.error(f"Model error: {e}")
        return ""

    placeholder = st.empty()
    collected = ""
    for chunk in stream:
        # DeltaContent has attribute 'content'
        delta = getattr(chunk.choices[0].delta, 'content', '') or ''
        collected += delta
        placeholder.markdown(f"**Bot:** {collected}")
    return collected

# --- 6️⃣ Input & Send button ---
prompt = st.text_input("Your question:", key="input_box")
if st.button("Send"):
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        # Display user message
        st.chat_message("user").write(prompt)
        # Stream and display bot response
        with st.spinner("Thinking..."):
            answer = stream_response(prompt)
        # Save to history
        if answer:
            st.session_state.history.append(("assistant", answer))

# --- 7️⃣ Display full chat history ---
if st.session_state.history:
    st.markdown("---")
    for role, msg in st.session_state.history:
        st.chat_message(role).write(msg)
