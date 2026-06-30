import streamlit as st
import uuid
import requests
from datetime import datetime
API_BASE = "http://localhost:8000"
st.set_page_config(
    page_title="AI Support Agent",
    page_icon="🤖",
    layout="centered"
)
st.markdown("""
<style>
body {
    background-color: #f7f7f9;
}
.chat-container {
    max-width: 900px;
    margin: auto;
}
.session-box {
    padding: 1rem;
    border-radius: 8px;
    font-size: 0.9rem;
}
footer {visibility: hidden;}
#MainMenu {visibility: hidden;}
</style>
""", unsafe_allow_html=True)
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
    st.session_state.messages = []
    st.session_state.started_at = datetime.now()
with st.sidebar:
    st.title("⚙️ Session")
    st.markdown(
        f"""
        <div class="session-box">
        <b>Session ID</b><br>
        {st.session_state.session_id[:8]}...<br><br>
        <b>Started</b><br>
        {st.session_state.started_at.strftime('%Y-%m-%d %H:%M:%S')}<br><br>
        <b>Messages</b><br>
        {len(st.session_state.messages)}
        </div>
        """,
        unsafe_allow_html=True
    )
    st.divider()
    if st.button("🗑️ Clear Chat"):
        st.session_state.messages = []
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.started_at = datetime.now()
        st.rerun()
    st.divider()
    st.markdown("### 💡 Try asking")
    examples = [
        "Where is my order ORD-1001?",
        "When will it be delivered?",
        "What is your refund policy?",
        "How do I return an item?"
    ]
    for q in examples:
        if st.button(q):
            st.session_state.example = q
            st.rerun()
st.title("🤖 AI Support Agent")
st.caption("A production-style AI customer support assistant")
st.divider()
if not st.session_state.messages:
    st.info(
        "👋 Welcome! Ask about order status, refunds, payments, or general support questions."
    )
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
if "example" in st.session_state:
    user_input = st.session_state.example
    del st.session_state.example
else:
    user_input = st.chat_input("Type your message...")
if user_input:
    st.session_state.messages.append(
        {"role": "user", "content": user_input}
    )
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            try:
                res = requests.post(
                    f"{API_BASE}/agent/chat",
                    json={"session_id": st.session_state.session_id, "message": user_input},
                    timeout=30
                )
                res.raise_for_status()
                reply = res.json()["reply"]
                st.markdown(reply)
                st.session_state.messages.append(
                    {"role": "assistant", "content": reply}
                )
            except Exception as e:
                error_text = "❌ Something went wrong. Please try again."
                st.error(error_text)
                st.session_state.messages.append(
                    {"role": "assistant", "content": error_text}
                )
st.divider()
st.caption(
    "Built with FastAPI, Groq LLM, FAISS, and Streamlit • Production-style AI agent"
)