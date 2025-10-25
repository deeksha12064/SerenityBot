import os
import streamlit as st
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

# Load API key
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error("❌ GROQ_API_KEY missing in .env!")
    st.stop()

client = Groq(api_key=api_key)

# Streamlit UI
st.set_page_config(page_title="SerenityBot", page_icon="🌸", layout="wide")

st.markdown(
    """
    <style>
        body {
            background-color: #E36DA1;
        }
        .chat-message {
            padding: 1rem;
            border-radius: 1rem;
            margin-bottom: 1rem;
            max-width: 70%;
            word-wrap: break-word;
        }
        .user-msg {
            background-color: #C8A2C8;
            margin-left: auto;
            text-align: right;
        }
        .bot-msg {
            background-color: #CDA29B;
            margin-right: auto;
            text-align: left;
        }
        .summary-card {
            background-color: #fff;
            padding: 0.8rem;
            border-radius: 0.8rem;
            margin-bottom: 1rem;
            box-shadow: 0px 4px 6px rgba(0,0,0,0.1);
        }
        .summary-date {
            font-size: 0.85rem;
            color: gray;
        }
    </style>
    """,
    unsafe_allow_html=True
)

st.title("🌸 SerenityBot – Your AI Therapist")
st.write("Meet **Sunny**, your gentle therapist companion. Share your thoughts below 💭")

# Sidebar for Journal
st.sidebar.title("📖 Session Journal")
journal_file = "journal.txt"

# Show past summaries
if os.path.exists(journal_file):
    with open(journal_file, "r", encoding="utf-8") as f:
        summaries = f.read().strip().split("### ")
        for entry in summaries:
            if entry.strip():
                lines = entry.split("\n", 1)
                date = lines[0].strip()
                summary = lines[1].strip() if len(lines) > 1 else ""
                st.sidebar.markdown(
                    f"<div class='summary-card'><div class='summary-date'>📅 {date}</div><div>{summary}</div></div>",
                    unsafe_allow_html=True
                )

# 🗑️ Clear journal button
if st.sidebar.button("🗑️ Clear Journal"):
    if os.path.exists(journal_file):
        open(journal_file, "w").close()
        st.sidebar.success("✅ Journal cleared!")

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "assistant", "content": "Hi there! 🌸 How can I help you? What happened today?"}
    ]

# Chat input
user_input = st.chat_input("Type your thoughts here...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    with st.spinner("Sunny is reflecting..."):
        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": 
                        "You are Sunny, a professional yet warm AI therapist. "
                        "Always reply with empathy, reflection, and gentle professionalism. "
                        "At the end of each response, include 1–2 fitting emojis (🌸 must always be included)."
                    }
                ] + st.session_state.messages
            )
            ai_reply = response.choices[0].message.content
            st.session_state.messages.append({"role": "assistant", "content": ai_reply})

        except Exception as e:
            st.error(f"Error: {e}")

# Display conversation
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"<div class='chat-message user-msg'>👤 {msg['content']}</div>", unsafe_allow_html=True)
    else:
        st.markdown(f"<div class='chat-message bot-msg'>🌸 {msg['content']}</div>", unsafe_allow_html=True)

# End session button → generate summary
if st.button("📌 End Session & Save Summary"):
    with st.spinner("Sunny is writing your session summary..."):
        try:
            # Format chat history into readable text
            conversation_text = "\n".join(
                [f"User: {m['content']}" if m["role"] == "user" else f"Sunny: {m['content']}" 
                 for m in st.session_state.messages]
            )

            summary_response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[
                    {"role": "system", "content": 
                        "You are Sunny, a professional therapist. "
                        "Write a short, empathetic therapy session summary of the conversation. "
                        "Keep it under 6 sentences, warm, and concise."},
                    {"role": "user", "content": conversation_text}
                ]
            )
            summary = summary_response.choices[0].message.content

            # Save summary to journal
            with open(journal_file, "a", encoding="utf-8") as f:
                f.write(f"### Session on {datetime.now().strftime('%Y-%m-%d %H:%M')}\n{summary}\n")

            st.success("✅ Session summary saved to your Journal!")

        except Exception as e:
            st.error(f"Error: {e}")


