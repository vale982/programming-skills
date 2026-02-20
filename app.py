import streamlit as st
import json
import time
import pandas as pd
import os
from datetime import datetime

# -----------------------------
# CARICAMENTO DOMANDE
# -----------------------------
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)

# -----------------------------
# CONFIGURAZIONE PAGINA
# -----------------------------
st.set_page_config(page_title="Test Programming Skill", layout="wide")
st.markdown("""
    <style>
        /* Stile personalizzato per il pulsante "Chiedi aiuto all'AI" */
        div.stButton > button:first-child {
            background-color: #4da6ff !important;   /* azzurro */
            color: white !important;
            border-radius: 8px !important;
            padding: 10px 20px !important;
            font-size: 18px !important;
            border: none !important;
        }

        /* Hover effect */
        div.stButton > button:first-child:hover {
            background-color: #1a8cff !important;
            color: white !important;
        }
    </style>
""", unsafe_allow_html=True)


st.title("Valutazione delle skill di programmazione con / senza AI")

# -----------------------------
# SESSION STATE
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "intro"   # nuova fase iniziale

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "answers" not in st.session_state:
    st.session_state.answers = []

if "codice" not in st.session_state:
    st.session_state.codice = ""   # per pulire il text_area

# -----------------------------
# FASE INTRO: NOME + LINGUAGGIO
# -----------------------------
if st.session_state.fase == "intro":
    st.markdown(
    "<h2 style='font-size:28px; margin-bottom:10px;'>Inserisci i tuoi dati per iniziare</h2>",
    unsafe_allow_html=True
    )

    st.markdown(
        "<div style='font-size:20px; margin-bottom:5px;'>ID Utente (obbligatorio)</div>",
        unsafe_allow_html=True
    )
    utente = st.text_input("", "")

    
    st.markdown(
    "<div style='font-size:22px; margin-bottom:5px;'>Scegli il linguaggio</div>",
    unsafe_allow_html=True
    )

    linguaggio = st.selectbox("", list(QUESTIONS.keys()))


    if st.button("START"):

        if utente.strip() == "":
            st.warning("Inserisci un ID utente prima di iniziare.")
            st.stop()

        st.session_state.utente = utente
        st.session_state.linguaggio = linguaggio
        st.session_state.fase = "senza_ai"
        st.rerun()

    st.stop()

# -----------------------------
# LOGICA DOMANDE
# -----------------------------
utente = st.session_state.utente
linguaggio = st.session_state.linguaggio
domande = QUESTIONS[linguaggio]

modalita = "Senza AI" if st.session_state.fase == "senza_ai" else "Con AI"

# Messaggio quando inizia la fase AI
if st.session_state.fase == "con_ai" and st.session_state.current_index == 0:
    st.info("🔍 **Aiutati ora con l'AI**")

# Se abbiamo finito le domande della fase corrente
if st.session_state.current_index >= len(domande):

    # Fine fase SENZA AI → mostra messaggio + pulsante
    if st.session_state.fase == "senza_ai":
        st.success("Hai completato tutte le domande SENZA AI!")
        st.write("Ora inizierai le domande CON AI.")

        if st.button("Inizia domande con l'aiuto dell'AI"):
            st.session_state.fase = "con_ai"
            st.session_state.current_index = 0
            st.session_state.start_time = None
            st.rerun()

        st.stop()

    # Fine fase CON AI → fine esperimento
    else:
        st.success("Hai completato tutte le domande CON AI!")
        st.write("Esperimento completato.")
        st.stop()


# -----------------------------
# MOSTRA DOMANDA CORRENTE
# -----------------------------
domanda = domande[st.session_state.current_index]

st.subheader(f"Domanda {domanda['id']} (Livello {domanda['level']})")

st.markdown(
    f"<div style='font-size:22px; line-height:1.5;'>{domanda['text']}</div>",
    unsafe_allow_html=True
)


# -----------------------------
# TIMER
# -----------------------------
if st.session_state.start_time is None:
    st.session_state.start_time = time.time()

# -----------------------------
# AREA DI TESTO PER IL CODICE
# -----------------------------
codice = st.text_area(
    "Scrivi il tuo codice qui",
    height=200,
    key=f"codice_{st.session_state.current_index}"
)


# -----------------------------
# AI SUGGESTION (solo se fase con AI)
# -----------------------------
ai_suggestion = None
if modalita == "Con AI":
    copilot_url = "https://copilot.microsoft.com/"
    st.markdown(
        f"""
        <a href="{copilot_url}" target="_blank">
            <button style="
                background-color:#4da6ff;
                color:white;
                padding:10px 20px;
                border:none;
                border-radius:8px;
                font-size:18px;
                cursor:pointer;
            ">
                Chiedi aiuto all'AI
            </button>
        </a>
        """,
        unsafe_allow_html=True
    )


# -----------------------------
# INVIO RISPOSTA
# -----------------------------
if st.button("Invia risposta"):
    end_time = time.time()
    elapsed = end_time - st.session_state.start_time

    risposta = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "utente": utente,
        "linguaggio": linguaggio,
        "domanda_id": domanda["id"],
        "livello": domanda["level"],
        "modalita": modalita,
        "codice": codice,
        "tempo_secondi": elapsed,
        "ai_suggestion": ai_suggestion
    }

    # Salva in sessione
    st.session_state.answers.append(risposta)

    # -----------------------------
    # SALVATAGGIO SU UN UNICO CSV
    # -----------------------------
    filename = "risposte.csv"
    df = pd.DataFrame([risposta])

    if os.path.exists(filename):
        df.to_csv(filename, mode="a", header=False, index=False)
    else:
        df.to_csv(filename, index=False)

    st.success(f"Risposta salvata! Tempo impiegato: {elapsed:.2f} secondi")


    # Passa alla prossima domanda
    st.session_state.start_time = None
    st.session_state.current_index += 1
    st.rerun()
    
    
