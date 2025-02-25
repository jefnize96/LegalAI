from .llm import LLM
from .retrieval import Retriever
from .query_parser import QueryParser
import logging

# Logging visibile nella console (già impostato in app.py o utils.py, ma assicuriamo consistenza)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

class QueryProcessor:
    def __init__(self):
        logging.info("Inizializzazione QueryProcessor")
        try:
            self.llm = LLM()
            logging.info("LLM inizializzato")
            self.retriever = Retriever()
            logging.info("Retriever inizializzato")
            self.parser = QueryParser()
            logging.info("QueryParser inizializzato")
        except Exception as e:
            logging.error(f"Errore durante inizializzazione QueryProcessor: {str(e)}")
            raise

    def process(self, query):
        logging.info(f"Query ricevuta: {query}")
        saluti = ["ciao", "hello", "salve", "buongiorno", "buonasera"]
        if query.lower().strip() in saluti:
            logging.info("Rilevato saluto")
            return "Ciao! Sono LegalAI, il tuo assistente giuridico perfetto. Come posso aiutarti oggi? Chiedimi qualcosa di specifico, come 'Cosa dice l’articolo 2051 del Codice Civile?'"

        parsed = self.parser.parse(query)
        intent = parsed["intent"]
        entities = parsed["entities"]

        tipo = entities["tipo"]
        docs = self.retriever.search(query, tipo, intent)
        if not docs:
            logging.warning(f"Nessun risultato per: {query}")
            return "Non ho trovato informazioni pertinenti nel database per questa query."

        if len(docs) > 1 and intent != "compare":
            ids = [doc["id"] for doc in docs]
            logging.info(f"Ambiguità rilevata: {ids}")
            return (
                "Trovati più risultati. Specifica meglio il contesto (es. 'Codice Civile', 'Codice Penale', 'procedura') "
                "o chiedimi qualcosa di più preciso:\n" + "\n".join(ids)
            )

        docs_text = "\n".join([
            f"ID: {doc['id']} | Tipo: {doc['type']} | Contesto: {doc['context']}\n"
            f"Testo: {doc['text']}\n"
            f"Dettagli: {doc['structure']}"
            for doc in docs
        ])
        response = self.llm.generate_response(query, docs_text)
        logging.info(f"Risposta generata: {response}")
        return response