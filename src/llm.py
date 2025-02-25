from transformers import pipeline
import torch

class LLM:
    def __init__(self):
        # Usa un modello più potente e adatto all'italiano
        self.model = pipeline(
            "text-generation",
            model="mistralai/Mixtral-8x7B-Instruct-v0.1",
            device="cuda" if torch.cuda.is_available() else "cpu"
        )

    def generate_response(self, query, docs_text):
        prompt = f"""Analizza la seguente query legale e tutte le informazioni disponibili dal database:

Query: {query}

Informazioni disponibili:
{docs_text}

Istruzioni per la risposta:
1. Analizza tutte le fonti fornite (leggi, sentenze, procedure)
2. Integra le informazioni in modo coerente
3. Se ci sono interpretazioni giurisprudenziali, considerale nell'analisi
4. Se ci sono procedure correlate, includile nella risposta
5. Organizza la risposta in modo logico e strutturato
6. Cita le fonti specifiche quando appropriato
7. Usa SOLO le informazioni fornite, senza aggiungere interpretazioni non supportate

Rispondi in modo chiaro, completo e ben strutturato in italiano:"""

        response = self.model(
            prompt,
            max_length=2000,
            temperature=0.7,
            do_sample=True,
            top_p=0.95,
            num_return_sequences=1
        )
        return response[0]["generated_text"].split("Rispondi")[1].strip()