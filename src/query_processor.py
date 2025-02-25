from .llm import LLM
from .retrieval import Retriever
from .query_parser import QueryParser
import logging

# Logging visibile nella console
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

    def check_ambiguity(self, query, docs):
        """Analizza l'ambiguità della query e dei risultati"""
        ambiguity_info = {
            "is_ambiguous": False,
            "reason": None,
            "suggestions": [],
            "conflicts": []
        }

        # Caso 1: Ambiguità per mancanza di contesto specifico
        if len(docs) > 3:  # Troppi risultati rilevanti
            common_contexts = set()
            for doc in docs:
                context = doc["context"].split(",")[0].strip()  # Prendi il contesto principale
                common_contexts.add(context)
            
            if len(common_contexts) > 1:
                ambiguity_info.update({
                    "is_ambiguous": True,
                    "reason": "contesto_multiplo",
                    "suggestions": [
                        f"Specifica il contesto tra: {', '.join(common_contexts)}",
                        "Aggiungi più dettagli alla tua domanda",
                        "Specifica il codice di riferimento (es. Codice Civile, Codice Penale)"
                    ]
                })

        # Caso 2: Ambiguità per conflitto temporale
        temporal_conflicts = []
        for doc in docs:
            if "data_vigore" in doc["structure"]:
                temporal_conflicts.append({
                    "id": doc["id"],
                    "data": doc["structure"]["data_vigore"]
                })
        
        if len(temporal_conflicts) > 1:
            ambiguity_info.update({
                "is_ambiguous": True,
                "reason": "conflitto_temporale",
                "conflicts": temporal_conflicts,
                "suggestions": [
                    "Specifica il periodo temporale di interesse",
                    "Indica se vuoi la versione attuale o una versione storica"
                ]
            })

        # Caso 3: Ambiguità per termini polisemici nel contesto legale
        legal_terms = self.parser.extract_legal_terms(query)
        term_conflicts = {}
        
        for term in legal_terms:
            term_docs = [doc for doc in docs if term.lower() in doc["text"].lower()]
            if len(term_docs) > 1:
                contexts = set(doc["context"] for doc in term_docs)
                if len(contexts) > 1:
                    term_conflicts[term] = list(contexts)

        if term_conflicts:
            ambiguity_info.update({
                "is_ambiguous": True,
                "reason": "termini_ambigui",
                "conflicts": term_conflicts,
                "suggestions": [
                    f"Il termine '{term}' ha diversi significati in: {', '.join(contexts)}"
                    for term, contexts in term_conflicts.items()
                ]
            })

        return ambiguity_info

    def handle_ambiguity(self, query, ambiguity_info):
        """Gestisce l'ambiguità fornendo una risposta appropriata"""
        if not ambiguity_info["is_ambiguous"]:
            return None

        response_parts = ["Ho trovato alcune ambiguità nella tua domanda:"]

        if ambiguity_info["reason"] == "contesto_multiplo":
            response_parts.append("\nLa tua domanda potrebbe riferirsi a diversi contesti legali.")
            response_parts.append("Per aiutarti meglio, potresti:")
            response_parts.extend(f"- {sugg}" for sugg in ambiguity_info["suggestions"])

        elif ambiguity_info["reason"] == "conflitto_temporale":
            response_parts.append("\nHo trovato versioni diverse della normativa nel tempo.")
            response_parts.append("Potresti specificare:")
            response_parts.extend(f"- {sugg}" for sugg in ambiguity_info["suggestions"])

        elif ambiguity_info["reason"] == "termini_ambigui":
            response_parts.append("\nAlcuni termini nella tua domanda hanno significati diversi in contesti legali diversi:")
            for term, contexts in ambiguity_info["conflicts"].items():
                response_parts.append(f"\n'{term}' può riferirsi a:")
                response_parts.extend(f"- {ctx}" for ctx in contexts)

        response_parts.append("\nPuoi riformulare la domanda con più dettagli?")
        return "\n".join(response_parts)

    def process(self, query):
        logging.info(f"Query ricevuta: {query}")
        
        # Gestione saluti
        saluti = ["ciao", "hello", "salve", "buongiorno", "buonasera"]
        if query.lower().strip() in saluti:
            logging.info("Rilevato saluto")
            return "Ciao! Sono LegalAI, il tuo assistente giuridico perfetto. Come posso aiutarti oggi?"

        # Parse della query
        parsed = self.parser.parse(query)
        
        # Ricerca documenti
        docs = self.retriever.search(query, intent=parsed["intent"])
        
        # Controllo ambiguità
        ambiguity_info = self.check_ambiguity(query, docs)
        if ambiguity_info["is_ambiguous"]:
            return self.handle_ambiguity(query, ambiguity_info)

        # Organizza i documenti per tipo
        organized_docs = {
            "leggi": [],
            "sentenze": [],
            "procedure": [],
            "altri": []
        }
        
        for doc in docs:
            if doc["type"] == "legge":
                organized_docs["leggi"].append(doc)
            elif doc["type"] == "sentenza":
                organized_docs["sentenze"].append(doc)
            elif doc["type"] == "procedura":
                organized_docs["procedure"].append(doc)
            else:
                organized_docs["altri"].append(doc)

        # Costruisci il contesto strutturato
        context_parts = []
        
        if organized_docs["leggi"]:
            context_parts.append("Articoli di legge pertinenti:")
            for doc in organized_docs["leggi"]:
                context_parts.append(f"- {doc['id']}: {doc['text']}")
                context_parts.append(f"  Contesto: {doc['context']}")
        
        if organized_docs["sentenze"]:
            context_parts.append("\nInterpretazioni giurisprudenziali:")
            for doc in organized_docs["sentenze"]:
                context_parts.append(f"- Sentenza {doc['id']}:")
                context_parts.append(f"  {doc['text']}")
        
        if organized_docs["procedure"]:
            context_parts.append("\nProcedure correlate:")
            for doc in organized_docs["procedure"]:
                context_parts.append(f"- {doc['id']}:")
                context_parts.append(f"  {doc['text']}")

        full_context = "\n".join(context_parts)
        
        # Genera la risposta
        response = self.llm.generate_response(query, full_context)
        logging.info(f"Risposta generata: {response}")
        return response