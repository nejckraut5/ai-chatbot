import os
import streamlit as st
from groq import Groq
from datetime import datetime

st.set_page_config(page_title="AI Asistent", layout="centered")

# Preveri API ključ
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error("❌ API ključ ni nastavljen! Dodaj GROQ_API_KEY v Streamlit Secrets.")
    st.stop()

client = Groq(api_key=api_key)

# Sistem prompt – omejen na vsebino spletne strani
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

# Funkcija za pošiljanje vprašanja
def poslji_vprasanje():
    vnos = st.session_state.vnos.strip()
    if not vnos:
        return
    st.session_state.messages.append({"role": "user", "content": vnos})

    if len(st.session_state.messages) > 11:  # omejimo zgodovino
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
    st.session_state.vnos = ""  # počisti input po pošiljanju

# Naslov
st.header("AI Asistent")

# Input uporabnika
st.text_input(
    "Vprašaj me:",
    key="vnos",
    placeholder="Vprašajte o hrani, športu ali avtom...",
    on_change=poslji_vprasanje
)

st.divider()

# Prikaz zgodovine pogovora (najnovejše spodaj)
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    elif msg["role"] == "user":
        st.write(f"👤 {msg['content']}")
    else:
        st.write(f"🤖 {msg['content']}")

# Gumb za shranjevanje pogovora
if st.button("💾 Shrani pogovor"):
    with open("zgodovina_pogovora.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- Pogovor {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
    st.success("Pogovor je shranjen.")
