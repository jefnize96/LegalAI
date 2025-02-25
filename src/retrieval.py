import re
from sentence_transformers import SentenceTransformer
import faiss
import numpy as np
from .utils import load_database
from functools import lru_cache

class Retriever:
    def __init__(self, db_path="data/database.json"):
        self.model = SentenceTransformer("paraphrase-multilingual-MiniLM-L12-v2")
        self.db = load_database(db_path)
        self.embeddings = self.model.encode([f"{doc['text']} {doc['context']}" for doc in self.db])
        self.index = faiss.IndexFlatL2(self.embeddings.shape[1])
        self.index.add(np.array(self.embeddings))

    @lru_cache(maxsize=1000)
    def search_by_id(self, id):
        return [doc for doc in self.db if doc["id"] == id] or []

    @lru_cache(maxsize=1000)
    def search_semantic(self, query, k=10):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), k)
        return [self.db[i] for i in indices[0]]

    def search(self, query, tipo=None, intent=None):
        # Ricerca semantica iniziale più ampia
        results = self.search_semantic(query, k=10)
        
        # Filtraggio intelligente basato sul contesto
        filtered_results = []
        
        # Cerca riferimenti diretti (es. articoli citati)
        direct_refs = re.finditer(r"(CC|CP|Proc|Cass)-[A-Za-z0-9-]+", query)
        for ref in direct_refs:
            ref_results = self.search_by_id(ref.group(0))
            filtered_results.extend(ref_results)
            
            # Cerca anche documenti correlati (es. sentenze che citano l'articolo)
            for doc in self.db:
                if "riferimenti" in doc["structure"] and ref.group(0) in doc["structure"]["riferimenti"]:
                    filtered_results.append(doc)
        
        # Analisi semantica per trovare documenti correlati
        query_parts = query.lower().split()
        context_keywords = {
            "civile": ["CC-", "civile", "contratto", "risarcimento", "danno"],
            "penale": ["CP-", "penale", "reato", "pena"],
            "procedura": ["Proc-", "procedura", "processo"],
            "giurisprudenza": ["Cass-", "sentenza", "cassazione"]
        }
        
        # Aggiungi risultati basati sul contesto
        for result in results:
            # Verifica se il documento è rilevante per il contesto
            is_relevant = False
            for context_type, keywords in context_keywords.items():
                if any(kw in query_parts for kw in keywords) and \
                   any(kw in result["context"].lower() or kw in result["text"].lower() for kw in keywords):
                    is_relevant = True
                    break
            
            # Aggiungi documenti rilevanti che non sono già inclusi
            if is_relevant and result not in filtered_results:
                filtered_results.append(result)
        
        # Se non abbiamo trovato risultati diretti, usa i risultati semantici
        if not filtered_results:
            filtered_results = results[:5]  # Limita a 5 risultati più rilevanti
            
        return filtered_results
