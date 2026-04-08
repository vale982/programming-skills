import streamlit as st
import json
import time
import pandas as pd
import os
from datetime import datetime
import random
import gspread
from google.oauth2.service_account import Credentials


def get_sheet():
    scope = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive"
    ]

    creds = Credentials.from_service_account_info(
        st.secrets["gcp_service_account"],
        scopes=scope
    )

    client = gspread.authorize(creds)

    sheet = client.open_by_url(
        "https://docs.google.com/spreadsheets/d/1UYwvWyno6wP98t6bKckYjmHdP0W3ixi0Z_hPui5Lfyg"
    ).sheet1
    return sheet


# -----------------------------
# CARICAMENTO DOMANDE
# -----------------------------
with open("questions.json", "r", encoding="utf-8") as f:
    QUESTIONS = json.load(f)


# -----------------------------
# CONFIGURAZIONE PAGINA
# -----------------------------
st.set_page_config(page_title="Test Programming Skill", layout="wide")

st.title("Valutazione delle skill di programmazione con / senza AI")


# -----------------------------
# SESSION STATE
# -----------------------------
if "fase" not in st.session_state:
    st.session_state.fase = "intro"

if "current_index" not in st.session_state:
    st.session_state.current_index = 0

if "start_time" not in st.session_state:
    st.session_state.start_time = None

if "answers" not in st.session_state:
    st.session_state.answers = []

if "domande_random" not in st.session_state:
    st.session_state.domande_random = []

if "extra_q_done" not in st.session_state:
    st.session_state.extra_q_done = False


# -----------------------------
# FASE INTRO: NOME + LINGUAGGIO + 2 NUOVE DOMANDE
# -----------------------------
if st.session_state.fase == "intro":

    st.subheader("Inserisci i tuoi dati per iniziare")

    utente = st.text_input("ID Utente (obbligatorio)", "")

    linguaggio = st.selectbox("Scegli il linguaggio", list(QUESTIONS.keys()))

    # Nuova domanda 1
    esperienza_bool = st.radio(
        "Hai mai scritto codice in questo linguaggio?",
        ["Sì", "No"]
    )

    # Nuova domanda 2
    esperienza_livello = st.slider(
        "Quanto ti senti esperto da 1 a 5?",
        min_value=1, max_value=5, value=3
    )

    if st.button("START"):

        if utente.strip() == "":
            st.warning("Inserisci un ID utente prima di iniziare.")
            st.stop()

        st.session_state.utente = utente
        st.session_state.linguaggio = linguaggio
        st.session_state.esperienza_bool = esperienza_bool
        st.session_state.esperienza_livello = esperienza_livello

        # Randomizza le domande una sola volta
        domande = QUESTIONS[linguaggio]
        random.shuffle(domande)
        st.session_state.domande_random = domande

        st.session_state.fase = "senza_ai"
        st.rerun()

    st.stop()


# -----------------------------
# LOGICA DOMANDE
# -----------------------------
utente = st.session_state.utente
linguaggio = st.session_state.linguaggio
domande = st.session_state.domande_random

modalita = "Senza AI" if st.session_state.fase == "senza_ai" else "Con AI"


# -----------------------------
# FINE FASE SENZA AI
# -----------------------------
if st.session_state.current_index >= len(domande):

    if st.session_state.fase == "senza_ai":
        st.success("Hai completato tutte le domande SENZA AI!")
        st.write("Ora inizierai le domande CON AI.")

        if st.button("Inizia domande con l'aiuto dell'AI"):
            st.session_state.fase = "con_ai"
            st.session_state.current_index = 0
            st.session_state.start_time = None

            # Randomizza di nuovo per la fase AI
            domande = QUESTIONS[linguaggio]
            random.shuffle(domande)
            st.session_state.domande_random = domande

            st.rerun()

        st.stop()

    else:
        st.success("Hai completato tutte le domande CON AI!")
        st.write("Esperimento completato.")
        st.stop()


# -----------------------------
# MOSTRA DOMANDA CORRENTE
# -----------------------------
domanda = domande[st.session_state.current_index]

st.subheader(f"Domanda {domanda['id']}")

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
# AREA CODICE
# -----------------------------
codice = st.text_area(
    "Scrivi il tuo codice qui",
    height=200,
    key=f"codice_{st.session_state.current_index}"
)


# -----------------------------
# AI BUTTON (solo fase AI)
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
        "modalita": modalita,
        "codice": codice,
        "tempo_secondi": elapsed,
        "ai_suggestion": ai_suggestion,
        "esperienza_bool": st.session_state.esperienza_bool,
        "esperienza_livello": st.session_state.esperienza_livello
    }

    st.session_state.answers.append(risposta)

    # Salvataggio su Google Sheets
    sheet = get_sheet()
    sheet.append_row([
        risposta["timestamp"],
        risposta["utente"],
        risposta["linguaggio"],
        risposta["domanda_id"],
        risposta["modalita"],
        risposta["codice"],
        risposta["tempo_secondi"],
        risposta["ai_suggestion"],
        risposta["esperienza_bool"],
        risposta["esperienza_livello"]
    ])

    st.success(f"Risposta salvata! Tempo impiegato: {elapsed:.2f} secondi")

    st.session_state.start_time = None
    st.session_state.current_index += 1
    st.rerun()
