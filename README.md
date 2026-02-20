# programming-skills
# Test di Valutazione delle Skill di Programmazione

Questa applicazione Streamlit permette di valutare le capacità di programmazione degli utenti attraverso due fasi:

1. **Senza AI** – l’utente risponde alle domande senza assistenza.
2. **Con AI** – l’utente può chiedere aiuto a Copilot tramite un link dedicato.

Le risposte vengono salvate in un file CSV insieme a:
- ID utente
- Linguaggio scelto
- Testo della risposta
- Tempo impiegato
- Modalità (con o senza AI)
- Timestamp dell’invio

## Come eseguire l’app

### In locale
```bash
pip install -r requirements.txt
streamlit run app.py
