import os
import streamlit as st
from groq import Groq
from datetime import datetime

# =========================
# Nastavitve strani
# =========================
st.set_page_config(page_title="AI Asistent", layout="centered")
st.markdown(
    "<h2 style='text-align:center; color:#FF6A00;'>AI Asistent</h2>", 
    unsafe_allow_html=True
)

# API ključ
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error(
        "❌ API ključ ni nastavljen! Dodaj GROQ_API_KEY v Streamlit Secrets."
    )
    st.stop()

client = Groq(api_key=api_key)

# =========================
# CSS za chat okno
# =========================
st.markdown("""
<style>
/* Belo ozadje chat okna */
main > div.block-container {
    background-color: white;
    border: 3px solid #FF6A00; /* oranžna obroba */
    border-radius: 12px;
    padding: 16px;
}

/* Besedilo uporabnika in AI-ja */
div.stTextInput > label, div.stButton > button {
    font-size: 16px;
}

/* Scrollbar za zgodovino pogovora */
[data-testid="stVerticalBlock"] {
    max-height: 400px;
    overflow-y: auto;
}
</style>
""", unsafe_allow_html=True)

# =========================
# SYSTEM PROMPT
# =========================
SYSTEM_PROMPT = """
Si AI Asistent za to spletno stran. Komuniciraš samo o vsebini spletne strani:
1️⃣ HRANA – Avtor govori o hrani, ki jo rad je in zakaj.
2️⃣ ŠPORT – Nogomet, košarka, odbojka.
3️⃣ AVTO – Toyota Aygo MK1, najboljši avto.

Če te vpraša kaj drugega, vljudno poveš, da nimaš informacij. 
Odgovori so izključno v slovenščini, pregledni in slovnično pravilni.
"""

# =========================
# Session state
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": SYSTEM_PROMPT}]

# =========================
# Funkcija za pošiljanje vprašanja
# =========================
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
# UI za vnos uporabnika
# =========================
st.text_input(
    "Vprašaj me nekaj o spletni strani:",
    key="vnos",
    placeholder="Vprašajte o hrani, športu ali avtom...",
    on_change=poslji_vprasanje
)

st.divider()

# =========================
# Prikaz pogovora (novejše na vrhu)
# =========================
for msg in reversed(st.session_state.messages):
    if msg["role"] == "system":
        continue
    elif msg["role"] == "user":
        st.markdown(f"**👤 Vi:** {msg['content']}")
    else:
        st.markdown(f"**🤖 AI:** {msg['content']}")

# =========================
# Shrani pogovor
# =========================
if st.button("💾 Shrani pogovor"):
    with open("zgodovina_pogovora.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- Pogovor {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
    st.success("Pogovor je shranjen.")
