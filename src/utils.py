import json
import logging
import os

# Crea la cartella logs se non esiste
log_dir = "logs"
os.makedirs(log_dir, exist_ok=True)
log_file = os.path.join(log_dir, "legalai.log")

logging.basicConfig(
    filename=log_file,
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

def validate_entry(entry, db=None):
    required_base = {"id", "type", "text", "context", "structure"}
    if not all(field in entry for field in required_base):
        raise ValueError(f"Campi base mancanti: {required_base - set(entry.keys())}")
    
    required_structure = {
        "legge": ["codice", "libro", "titolo", "capo", "articolo", "commi"],
        "procedura": ["evento", "steps"],
        "sentenza": ["numero", "anno", "sezione", "riferimenti"],
        "circolare": ["ente", "numero", "data"]
    }
    tipo = entry["type"]
    if tipo not in required_structure:
        raise ValueError(f"Tipo non valido: {tipo}")
    
    structure = entry["structure"]
    missing = [field for field in required_structure[tipo] if field not in structure]
    if missing:
        raise ValueError(f"Campi mancanti in structure per {tipo}: {missing}")
    
    if not isinstance(entry["id"], str) or "-" not in entry["id"]:
        raise ValueError(f"ID non valido: {entry['id']}")
    
    if tipo == "sentenza" and db:
        refs = structure.get("riferimenti", [])
        for ref in refs:
            if not any(doc["id"] == ref for doc in db):
                raise ValueError(f"Riferimento non trovato nel database: {ref}")
    
    return True

def load_database(db_path):
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        validate_entry(entry, data)
    logging.info(f"Database caricato con successo: {len(data)} entries")
    return data

def update_database(db_path, new_data):
    current_db = load_database(db_path)
    for entry in new_data:
        validate_entry(entry, current_db + new_data)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    return load_database(db_path)