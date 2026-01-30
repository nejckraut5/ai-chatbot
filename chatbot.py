import os
import streamlit as st
from groq import Groq

# =========================
# OSNOVNE NASTAVITVE
# =========================
st.set_page_config(page_title="AI Klepetalnik", layout="centered")
st.title("AI pomočnik 🌟")

# API ključ
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    st.error(
        "❌ API ključ ni nastavljen. Dodaj GROQ_API_KEY v Streamlit Cloud → Secrets."
    )
    st.stop()

client = Groq(api_key=api_key)

# =========================
# SYSTEM PROMPT
# =========================

SYSTEM_PROMPT = """
Si AI chatbot, ki deluje IZKLJUČNO kot pomočnik za to spletno stran.
📄 SPLETNA STRAN IMA 3 STRANI:

1️⃣ HRANA – Avtor govori o hrani, ki jo rad je in zakaj.
2️⃣ ŠPORT – Nogomet, košarka, odbojka.
3️⃣ AVTO – Toyota Aygo MK1, najboljši avto.

❗ PRAVILA:
- Odgovarjaš SAMO o tej vsebini.
- Vljudno zavrneš zunanje teme.
- Izključno v slovenščini.
- Jasno, pregledno, slovnično pravilno.
- Spomin znotraj seje.
"""

# =========================
# SESSION STATE
# =========================
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": SYSTEM_PROMPT}
    ]

# =========================
# FUNKCIJA ZA POŠILJANJE VPRAŠANJA
# =========================
def poslji_vprasanje():
    vnos = st.session_state.vnos.strip()
    if not vnos:
        return

    st.session_state.messages.append({"role": "user", "content": vnos})

    # omejitev zgodovine (system + 10 sporočil)
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
# UPORABNIŠKI VNOS
# =========================
st.text_input(
    "Vprašaj me nekaj o spletni strani:",
    key="vnos",
    placeholder="Vprašajte o hrani, športu ali avtom...",
    on_change=poslji_vprasanje
)

st.divider()

# =========================
# PRIKAZ POGOVORA (NOVEJŠE NA VRHU)
# =========================
# Obrnemo seznam tako, da je najnovejše sporočilo na vrhu
for msg in reversed(st.session_state.messages):
    if msg["role"] == "system":
        continue
    elif msg["role"] == "user":
        st.markdown(f"**👤 Vi:** {msg['content']}")
    else:
        st.markdown(f"**🤖 AI:** {msg['content']}")

# =========================
# SHRANJEVANJE POGOVORA
# =========================
if st.button("💾 Shrani pogovor"):
    with open("zgodovina_pogovora.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- Pogovor {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for msg in st.session_state.messages:
            if msg["role"] != "system":
                f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
    st.success("Pogovor je shranjen.")
