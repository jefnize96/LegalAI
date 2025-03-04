import spacy

nlp = spacy.load("it_core_news_lg")

class QueryParser:
    def __init__(self):
        self.nlp = nlp

    def parse(self, query):
        doc = self.nlp(query)
        intent = "info"
        entities = {"codice": None, "articolo": None, "tipo": None, "evento": None}

        for token in doc:
            if "confronta" in token.text.lower() or "differenze" in token.text.lower():
                intent = "compare"
            if token.text.lower() in ["codice civile", "codice penale"]:
                entities["codice"] = token.text.lower()
            if "articolo" in token.text.lower() and token.head.is_digit:
                entities["articolo"] = token.head.text
            if token.text.lower() in ["procedura", "sentenza", "circolare"]:
                entities["tipo"] = token.text.lower()
            if "incendio" in token.text.lower():
                entities["evento"] = "Incendio"

        return {"intent": intent, "entities": entities}