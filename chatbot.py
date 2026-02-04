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
Chatbot je specializiran IZKLJUČNO za vsebino posamezne spletne strani.

Dovoljene strani in vsebine:
1️⃣ HRANA – spletna stran je namenjena hrani, ki jo avtor rad je, s predstavitvijo njegovih najljubših jedi in razlogov, zakaj jih ima rad.
2️⃣ ŠPORT – spletna stran pokriva športe, ki jih avtor rad spremlja: nogomet, košarka, odbojka, s poudarkom na osebnih preferencah in interesih.
3️⃣ AVTO – spletna stran je posvečena avtomobilom, posebej Toyota Aygo MK1, ki ga avtor smatra za najboljšega avto, z opisom značilnosti in razlogov.
"""

ZAVRNITVENI_ODGOVOR = (
    "Za to temo nimam informacij. "
    "Pomagam lahko samo z vprašanji, ki so povezana z vsebino teh spletnih strani."
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
        color: black;
    }

    body, p, span, div, label {
        color: black !important;
    }

    h1, h2, h3 {
        color: black;
    }

    div[data-testid="stButton"] > button {
        background-color: white !important;
        color: black !important;
        border: 1px solid black !important;
        border-radius: 6px !important;
    }

    div[data-testid="stButton"] > button:hover {
        background-color: white !important;
        color: black !important;
        border: 1px solid black !important;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# ===============================
# NASLOV STRANI
# ===============================

st.markdown(
    "<h1 style='text-align:center;'>AI asistent 💬</h1>",
    unsafe_allow_html=True
)

st.markdown(
    "<p style='text-align:center;color:gray;'>Podpora izključno za vsebino posameznih spletnih strani: Hrana, Šport, Avto</p>",
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
Ti si AI asistent za te spletne strani.

STROGA PRAVILA:
1. Odgovarjaš IZKLJUČNO v slovenščini.
2. Odgovarjaš SAMO na teme, povezane s posamezno stranjo:
   - HRANA: vsebina o hrani, ki jo avtor rad je.
   - ŠPORT: nogomet, košarka, odbojka.
   - AVTO: Toyota Aygo MK1 kot najboljši avto.
3. Če vprašanje NI povezano z dovoljenimi temami,
   vedno odgovoriš z:
   "{ZAVRNITVENI_ODGOVOR}"
4. Odgovori morajo biti:
   - jasni
   - pregledni
   - slovnično pravilni
   - vljudni
5. Ne ugibaš in ne izmišljuješ vsebine.
6. Znotraj seje si zapomniš pogovor.

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
    placeholder="Vprašajte nekaj o teh spletnih straneh …",
    on_change=poslji_vprasanje
)

# ===============================
# IZPIS POGOVORA (najnovejše zgoraj)
# ===============================

st.subheader("Pogovor")

# Obračamo seznam, da se najnovejše sporočilo prikaže na vrhu
for msg in reversed(st.session_state.messages):
    if msg["role"] == "system":
        continue

    if msg["role"] == "user":
        st.markdown(
            f"<div style='background-color:#e0f2fe; padding:10px; border-radius:10px;'>Vi: {msg['content']}</div>",
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f"<div style='background-color:#fde8d0; padding:10px; border-radius:10px;'><strong style='color:orange;'>Chatbot:</strong> {msg['content']}</div>",
            unsafe_allow_html=True
        )

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
