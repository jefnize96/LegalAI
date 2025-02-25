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
    def search_semantic(self, query, k=3):
        query_embedding = self.model.encode([query])
        distances, indices = self.index.search(np.array(query_embedding), k)
        return [self.db[i] for i in indices[0]]

    def search(self, query, tipo=None, intent="info"):
        id_match = re.search(r"(CC|CP|Proc|Cass)-[A-Za-z0-9-]+", query)
        if id_match:
            results = self.search_by_id(id_match.group(0))
            if results:
                return results

        results = self.search_semantic(query, k=5)
        if tipo:
            results = [r for r in results if r["type"] == tipo]
        
        if "Codice Civile" in query:
            results = [r for r in results if "CC-" in r["id"]]
        elif "Codice Penale" in query:
            results = [r for r in results if "CP-" in r["id"]]
        elif any(w in query.lower() for w in ["procedura", "caso di", "fare in"]):
            results = [r for r in results if "Proc-" in r["id"]]
        elif "sentenza" in query.lower():
            results = [r for r in results if "Cass-" in r["id"]]
        
        return results
