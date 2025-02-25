from transformers import pipeline

class LLM:
    def __init__(self):
        # Placeholder: Sostituisci con un modello reale per produzione (es. Mistral)
        self.model = pipeline("text-generation", model="facebook/opt-350m", device=-1)

    def generate_response(self, query, docs_text):
        prompt = (
            f"Query: {query}\n"
            f"Dati: {docs_text}\n"
            "Rispondi in italiano usando SOLO i dati forniti, senza aggiungere informazioni o interpretazioni non presenti. "
            "Se i dati sono insufficienti, rispondi: 'Dati insufficienti per rispondere alla query.'"
        )
        response = self.model(prompt, max_length=500, do_sample=False, num_return_sequences=1)
        return response[0]["generated_text"].split("Rispondi in italiano")[1].strip()
