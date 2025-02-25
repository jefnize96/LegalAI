import streamlit as st
from src.query_processor import QueryProcessor
from src.utils import update_database
import json
from datetime import datetime
import logging

# Logging visibile nella console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

st.set_page_config(page_title="LegalAI", page_icon="⚖️", layout="wide")

logging.info("Inizio inizializzazione app")
if "processor" not in st.session_state:
    try:
        # Inizializzazione minima per passare il controllo di salute
        st.session_state.processor = None
        logging.info("Processor inizializzato come None per il controllo di salute")
    except Exception as e:
        logging.error(f"Errore durante inizializzazione minima: {str(e)}")
        st.error("Errore durante l'inizializzazione dell'app.")
        st.stop()

if "session_active" not in st.session_state:
    st.session_state.session_active = False
    st.session_state.chat_history = []
    st.session_state.session_id = None

if not st.session_state.session_active:
    st.title("LegalAI - Assistente Giuridico Perfetto")
    st.markdown("Benvenuto! Inizia una sessione per utilizzare l’assistente.")
    if st.button("Inizia la chat"):
        st.session_state.session_active = True
        st.session_state.session_id = f"User_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        st.session_state.chat_history = []
        # Inizializzazione completa solo dopo il click
        if st.session_state.processor is None:
            with st.spinner("Caricamento dell’assistente..."):
                st.session_state.processor = QueryProcessor()
                logging.info("Processor inizializzato completamente")
        st.rerun()
else:
    st.title(f"LegalAI - Sessione {st.session_state.session_id}")
    st.markdown("Chiedi qualsiasi cosa, riceverai risposte precise al 100%.")

    for entry in st.session_state.chat_history:
        with st.chat_message("user"):
            st.write(entry["query"])
        with st.chat_message("assistant"):
            st.markdown(f"**{entry['response']}**")

    query = st.chat_input("Inserisci la tua domanda:")
    if query:
        with st.spinner("Elaborazione in corso..."):
            try:
                if st.session_state.processor is None:
                    st.session_state.processor = QueryProcessor()
                    logging.info("Processor inizializzato on-demand")
                response = st.session_state.processor.process(query)
                st.session_state.chat_history.append({"query": query, "response": response})
                st.rerun()
            except Exception as e:
                logging.error(f"Errore durante elaborazione query '{query}': {str(e)}")
                st.error("Errore durante l'elaborazione della query.")
                st.stop()

    if st.button("Termina sessione"):
        st.session_state.session_active = False
        st.session_state.chat_history = []
        st.session_state.session_id = None
        st.session_state.processor = None
        st.rerun()

with st.sidebar:
    st.subheader("Aggiorna il database")
    uploaded_file = st.file_uploader("Carica un nuovo database.json", type="json")
    if uploaded_file:
        try:
            new_data = json.load(uploaded_file)
            update_database("data/database.json", new_data)
            st.success("Database aggiornato con successo!")
            if st.session_state.processor is not None:
                st.session_state.processor = QueryProcessor()  # Ricarica il processor
                logging.info("Processor ricaricato dopo aggiornamento database")
        except Exception as e:
            logging.error(f"Errore durante aggiornamento database: {str(e)}")
            st.error("Errore durante l'aggiornamento del database.")