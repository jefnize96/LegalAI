from .llm import LLM
from .retrieval import Retriever
from .query_parser import QueryParser
import logging

class QueryProcessor:
    def __init__(self):
        self.llm = LLM()
        self.retriever = Retriever()
        self.parser = QueryParser()

    def process(self, query):
        logging.info(f"Query ricevuta: {query}")
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
                "Trovati più risultati. Specifica meglio il contesto (es. 'Codice Civile', 'Codice Penale', 'procedura'):\n"
                + "\n".join(ids)
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
