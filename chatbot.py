import os
import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="AI Asistent", layout="centered")

# API ključ
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ API ključ ni nastavljen! Dodaj GROQ_API_KEY v Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

SYSTEM_PROMPT = """
Si AI Asistent za to spletno stran. Komuniciraš samo o vsebini spletne strani:
1️⃣ HRANA – Avtor govori o hrani, ki jo rad je in zakaj.
2️⃣ ŠPORT – Nogomet, košarka, odbojka.
3️⃣ AVTO – Toyota Aygo MK1, najboljši avto.

Če te vpraša kaj drugega, vljudno poveš, da nimaš informacij. 
Odgovori so izključno v slovenščini, pregledni in slovnično pravilni.
"""

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

def poslji_vprasanje():
    vnos = st.session_state.vnos.strip()
    if not vnos:
        return
    st.session_state.messages.append({"role": "user", "content": vnos})
    if len(st.session_state.messages) > 11:
        st.session_state.messages.pop(1)
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )
        answer = response.choices[0].message.content
    except Exception:
        answer = "Prišlo je do tehnične napake."
    st.session_state.messages.append({"role": "assistant", "content": answer})
    st.session_state.vnos = ""

# =========================
# CSS za celoten chat bot
# =========================
st.markdown("""
<style>

.chat-title {
    text-align: center;
    color: #FF6A00;
    font-size: 24px;
    font-weight: bold;
    margin-bottom: 12px;
}
.chat-msg {
    padding: 8px 12px;
    margin-bottom: 8px;
    border-radius: 8px;
}
.chat-msg.user {
    background-color: #f0f0f0;
    text-align: right;
}
.chat-msg.assistant {
    background-color: #fff3e0;
    text-align: left;
}
.chat-history {
    max-height: 400px;
    overflow-y: auto;
}
.stTextInput>div>input {
    background-color: white !important;
}
</style>
""", unsafe_allow_html=True)

# =========================
# Chat container
# =========================
st.markdown('<div class="chat-box">', unsafe_allow_html=True)
st.markdown('<div class="chat-title">AI Asistent</div>', unsafe_allow_html=True)

st.text_input(
    "Vprašaj me:",
    key="vnos",
    placeholder="Vprašajte o hrani, športu ali avtom...",
    on_change=poslji_vprasanje
)

st.divider()

st.markdown('<div class="chat-history">', unsafe_allow_html=True)
for msg in reversed(st.session_state.messages):
    if msg["role"] == "system":
        continue
    elif msg["role"] == "user":
        st.markdown(f'<div class="chat-msg user">👤 {msg["content"]}</div>', unsafe_allow_html=True)
    else:
        st.markdown(f'<div class="chat-msg assistant">🤖 {msg["content"]}</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)
st.markdown('</div>', unsafe_allow_html=True)

# Shrani pogovor
if st.button("💾 Shrani pogovor"):
    with open("zgodovina_pogovora.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- Pogovor {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
    st.success("Pogovor je shranjen.")

