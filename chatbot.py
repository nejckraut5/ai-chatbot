import os
from datetime import datetime
import streamlit as st

# Poskusi uvoziti Groq
try:
    from groq import Groq
except ImportError:
    st.error("Paketa 'groq' ni nameščen. Preveri requirements.txt")
    st.stop()

# Naslov aplikacije
st.title("Klepetalnik AI 🌟")

# Preberi API ključ iz okolja
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    st.error(
        "API ključ ni nastavljen! "
        "Pojdi v Streamlit Cloud → Manage app → Settings → Secrets in dodaj GROQ_API_KEY."
    )
    st.stop()  # Zaustavi app, dokler ni ključ nastavljen

# Inicializacija Groq klienta
client = Groq(api_key=api_key)

# Inicializacija seznama sporočil v Streamlit session state
if "messages" not in st.session_state:
    st.session_state.messages = [
        {"role": "system", "content": "Si prijazen asistent, strokovnjak za informatiko."}
    ]

# Funkcija za pošiljanje sporočila in pridobitev odgovora
def poslji_vprasanje():
    vnos = st.session_state.vnos  # preberi tekst iz session state
    if not vnos:
        return

    st.session_state.messages.append({"role": "user", "content": vnos})

    # Omejitev dolžine zgodovine (največ 10 sporočil, brez začetnega system sporočila)
    if len(st.session_state.messages) > 11:
        st.session_state.messages.pop(1)

    try:
        odgovor = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=st.session_state.messages
        )

        ai_text = odgovor.choices[0].message.content
        st.session_state.messages.append({"role": "assistant", "content": ai_text})

        # Izpis AI odgovora
        st.write(f"**AI:** {ai_text}")

        # Izpis porabe žetonov, če obstaja
        if hasattr(odgovor, "usage"):
            usage = odgovor.usage
            st.write(
                f"**Poraba žetonov:** Vprašanje={usage['prompt_tokens']}, "
                f"Odgovor={usage['completion_tokens']}, Skupaj={usage['total_tokens']}"
            )

    except Exception as e:
        st.error(f"Prišlo je do napake: {e}")

    # Po pošiljanju počisti textbox
    st.session_state.vnos = ""

# UI za vnos uporabnika, sproži poslji_vprasanje ob Enter
st.text_input("Vi:", key="vnos", on_change=poslji_vprasanje)

# Prikaz celotnega pogovora
st.subheader("Zgodovina pogovora:")
for msg in st.session_state.messages:
    role = msg['role'].capitalize()
    st.write(f"**{role}:** {msg['content']}")

# Gumb za shranjevanje pogovora
if st.button("Shrani pogovor"):
    with open("zgodovina_pogovora.txt", "a", encoding="utf-8") as f:
        f.write(f"\n--- Pogovor ob {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ---\n")
        for msg in st.session_state.messages:
            f.write(f"{msg['role'].capitalize()}: {msg['content']}\n")
    st.success("Pogovor je shranjen v 'zgodovina_pogovora.txt'.")

