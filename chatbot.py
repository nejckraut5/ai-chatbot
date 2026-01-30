import os
from datetime import datetime
import streamlit as st

# ===============================
# UVOZ GROQ
# ===============================
try:
    from groq import Groq
except ImportError:
    st.error("Paket 'groq' ni nameščen. Preveri requirements.txt.")
    st.stop()

# ===============================
# OSNOVNI PODATKI O STRANI
# ===============================

PODROCJE_DELOVANJA = """
Ta chatbot je namenjen IZKLJUČNO pomoči uporabnikom te spletne strani.

Obseg delovanja:
- razlaga delovanja AI chatbota
- pomoč pri uporabi aplikacije
- osnovna tehnična podpora glede te strani
- vprašanja, povezana s funkcionalnostmi in namenom strani

Chatbot NE odgovarja na:
- splošna vprašanja
- osebne teme
- recepte, zdravje, pravo, finance
- teme, ki niso neposredno povezane s to spletno stranjo
"""

ZAVRNITVENI_ODGOVOR = (
    "Za to temo nimam informacij. "
    "Pomagam lahko samo z vprašanji, ki so povezana s to spletno stranjo in njenim delovanjem."
)

# ===============================
# STREAMLIT NASTAVITVE
# ===============================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="💬",
    layout="centered"
)

st.title("AI pomočnik 💬")
st.caption("Podpora izključno za to spletno stran")

# ===============================
# GROQ API KLJUČ
# ===============================

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error(
        "❌ API ključ ni nastavljen.\n\n"
        "V Streamlit Cloud pojdi na:\n"
        "**Manage app → Settings → Secrets**\n\n"
        "in dodaj:\n"
        "`GROQ_API_KEY = \"tvoj_kljuc\"`"
    )
    st.stop()

client = Groq(api_key=api_key)

# ===============================
# SESSION STATE (SPOMIN SEJE)
# ===============================
# Streamlit samodejno izbriše session state ob osvežitvi ali zapustitvi strani

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""
Ti si AI chatbot z NASLEDNJIMI STROGIMI PRAVILI:

1. Komuniciraš IZKLJUČNO v slovenščini.
2. Odgovarjaš LE na vprašanja, povezana s to spletno stranjo.
3. Če vprašanje ni v obsegu, vedno odgovoriš z:
   "{ZAVRNITVENI_ODGOVOR}"
4. Odgovori morajo biti:
   - jasni
   - pregledni
   - slovnično pravilni
   - prijazni in vljudni
5. Znotraj seje si zapomniš pogovor in razumeš podvprašanja.
6. Ne ugibaš, ne dodajaš informacij in ne izmišljuješ vsebine.

OPIS PODROČJA:
{PODROCJE_DELOVANJA}
"""
        }
    ]

# ===============================
# FUNKCIJA ZA POŠILJANJE VPRAŠANJA
# ===============================

def poslji_vprasanje():
    vnos = st.session_state.vnos.strip()

    if not vnos:
        return

    st.session_state.messages.append(
        {"role": "user", "content": vnos}
    )

    # omejitev zgodovine (1 system + 10 sporočil)
    if len(st.session_state.messages) > 11:
        st.session_state.messages.pop(1)

    try:
        odgovor = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )

        ai_odgovor = odgovor.choices[0].message.content.strip()

    except Exception:
        ai_odgovor = (
            "Prišlo je do tehnične napake. "
            "Prosimo, poskusite znova čez nekaj trenutkov."
        )

    st.session_state.messages.append(
        {"role": "assistant", "content": ai_odgovor}
    )

    st.session_state.vnos = ""

# ===============================
# UPORABNIŠKI VNOS
# ===============================

st.text_input(
    "Vaše vprašanje:",
    key="vnos",
    placeholder="Vprašajte nekaj o tej spletni strani …",
    on_change=poslji_vprasanje
)

# ===============================
# IZPIS POGOVORA
# ===============================

st.subheader("Pogovor")

for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue

    if msg["role"] == "user":
        st.markdown(f"**Vi:** {msg['content']}")
    else:
        st.markdown(f"**Chatbot:** {msg['content']}")

# ===============================
# SHRANJEVANJE (LOKALNO)
# ===============================

if st.button("💾 Shrani pogovor"):
    with open("zgodovina_pogovora.txt", "a", encoding="utf-8") as f:
        f.write(
            f"\n--- Pogovor {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n"
        )
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")

    st.success("Pogovor je shranjen.")
