# LegalAI
Assistente giuridico perfetto e multiutente basato su un LLM e un database manuale.

## Installazione
1. Clona il repository: `git clone <url>`
2. Crea un virtualenv: `python -m venv venv`
3. Attivalo: `venv\Scripts\activate` (Windows) o `source venv/bin/activate` (Linux/Mac)
4. Installa le dipendenze: `pip install -r requirements.txt`
5. Installa il modello spaCy: `python -m spacy download it_core_news_sm`
6. Avvia l'app: `streamlit run app.py`

## Uso
- Clicca "Inizia la chat" per creare una sessione personale.
- Inserisci query nella chat; ogni sessione è isolata.
- Termina la sessione con il pulsante dedicato.

## Aggiornamento Database
- Carica un nuovo `database.json` dalla sidebar (formato validato richiesto).

## Requisiti
- Python 3.8+
- GPU opzionale per LLM (modifica `llm.py` per un modello reale).
