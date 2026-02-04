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
# PODROČJE DELOVANJA CHATBOTA
# ===============================

PODROCJE_DELOVANJA = """
Chatbot je specializiran IZKLJUČNO za vsebino te spletne strani.

Dovoljena področja:
1️⃣ HRANA – Avtor govori o hrani, ki jo rad je in zakaj.
2️⃣ ŠPORT – Nogomet, košarka, odbojka.
3️⃣ AVTO – Toyota Aygo MK1 kot najboljši avto.

Chatbot NE odgovarja na:
- splošna vprašanja
- osebne teme
- zdravje, pravo, finance
- teme, ki niso povezane z zgornjimi področji
"""

ZAVRNITVENI_ODGOVOR = (
    "Za to temo nimam informacij. "
    "Pomagam lahko samo z vprašanji, ki so povezana z vsebino te spletne strani."
)

# ===============================
# STREAMLIT NASTAVITVE
# ===============================

st.set_page_config(
    page_title="AI Chatbot",
    page_icon="💬",
    layout="centered"
)

# ===============================
# OSNOVNI CSS (če okolje to podpira)
# ===============================

st.markdown(
    """
    <style>
    .stApp {
        background-color: white;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# NASLOV STRANI
# ===============================

st.markdown(
    "<h1 style='text-align:center;'>AI pomočnik 💬</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>Podpora izključno za to spletno stran</p>",
    unsafe_allow_html=True
)

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

if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "system",
            "content": f"""
Ti si AI asistent za to spletno stran.

STROGA PRAVILA:
1. Odgovarjaš IZKLJUČNO v slovenščini.
2. Odgovarjaš SAMO na teme, povezane s to spletno stranjo.
3. Dovoljene teme so:
   - HRANA (kaj avtor rad je in zakaj)
   - ŠPORT (nogomet, košarka, odbojka)
   - AVTO (Toyota Aygo MK1 kot najboljši avto)
4. Če vprašanje NI povezano z dovoljenimi temami,
   vedno odgovoriš z:
   "{ZAVRNITVENI_ODGOVOR}"
5. Odgovori morajo biti:
   - jasni
   - pregledni
   - slovnično pravilni
   - vljudni
6. Ne ugibaš, ne dodajaš informacij in si ne izmišljuješ vsebine.
7. Znotraj seje si zapomniš pogovor.

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
# VNOS UPORABNIKA
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
# SHRANJEVANJE POGOVORA
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

