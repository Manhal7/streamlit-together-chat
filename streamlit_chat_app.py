import os
import streamlit as st
from together import Together

# 1️⃣ Load API key from Streamlit secrets or environment variable
api_key = st.secrets.get("together_ai_api_key") or os.getenv("TOGETHER_API_KEY")
if not api_key:
    st.error("🔑 Missing Together AI API key.\nSet `together_ai_api_key` in `.streamlit/secrets.toml` or `TOGETHER_API_KEY` env var.")
    st.stop()

# 2️⃣ Ensure the Together client picks up the key
os.environ["TOGETHER_API_KEY"] = api_key
client = Together(api_key=api_key)

# 3️⃣ Initialize chat history
if "history" not in st.session_state:
    st.session_state.history = []

# 4️⃣ Page config & title
st.set_page_config(page_title="LLM Chat App", page_icon="🤖")
st.title("🤖 Streamlit LLM Chat with Together AI API")

# 5️⃣ Function to call the API
@st.cache_data
def generate_response(prompt: str) -> str:
    response = client.chat.completions.create(
        model="deepseek-ai/DeepSeek-V3",  # change or parameterize if needed
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content

# 6️⃣ User input and button
prompt = st.text_input("Your question:", key="input_box")
if st.button("Send"):
    if not prompt.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Fetching response..."):
            try:
                answer = generate_response(prompt)
                st.session_state.history.append((prompt, answer))
            except Exception as e:
                st.error(f"API error: {e}")

# 7️⃣ Display chat history
if st.session_state.history:
    st.markdown("---")
    st.header("Chat History")
    for user_msg, bot_msg in reversed(st.session_state.history):
        st.markdown(f"**You:** {user_msg}")
        st.markdown(f"**Bot:** {bot_msg}")
