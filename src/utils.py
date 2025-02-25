import json
import logging
import os

# Logging visibile nella console
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)

def validate_entry(entry, db=None):
    logging.info(f"Validating entry: {entry['id']}")
    required_base = {"id", "type", "text", "context", "structure"}
    if not all(field in entry for field in required_base):
        missing = required_base - set(entry.keys())
        logging.error(f"Campi base mancanti in {entry['id']}: {missing}")
        raise ValueError(f"Campi base mancanti: {missing}")
    
    required_structure = {
        "legge": ["codice", "libro", "titolo", "capo", "articolo", "commi"],
        "procedura": ["evento", "steps"],
        "sentenza": ["numero", "anno", "sezione", "riferimenti"],
        "circolare": ["ente", "numero", "data"]
    }
    tipo = entry["type"]
    if tipo not in required_structure:
        logging.error(f"Tipo non valido in {entry['id']}: {tipo}")
        raise ValueError(f"Tipo non valido: {tipo}")
    
    structure = entry["structure"]
    missing = [field for field in required_structure[tipo] if field not in structure]
    if missing:
        logging.error(f"Campi mancanti in structure per {entry['id']}: {missing}")
        raise ValueError(f"Campi mancanti in structure per {tipo}: {missing}")
    
    if not isinstance(entry["id"], str) or "-" not in entry["id"]:
        logging.error(f"ID non valido in {entry['id']}")
        raise ValueError(f"ID non valido: {entry['id']}")
    
    if tipo == "sentenza" and db:
        refs = structure.get("riferimenti", [])
        for ref in refs:
            if not any(doc["id"] == ref for doc in db):
                logging.error(f"Riferimento non trovato nel database per {entry['id']}: {ref}")
                raise ValueError(f"Riferimento non trovato nel database: {ref}")
    
    logging.info(f"Entry {entry['id']} validata con successo")
    return True

def load_database(db_path):
    logging.info(f"Caricamento database da {db_path}")
    with open(db_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    for entry in data:
        validate_entry(entry, data)
    logging.info(f"Database caricato con successo: {len(data)} entries")
    return data

def update_database(db_path, new_data):
    logging.info(f"Aggiornamento database in {db_path}")
    current_db = load_database(db_path)
    for entry in new_data:
        validate_entry(entry, current_db + new_data)
    with open(db_path, "w", encoding="utf-8") as f:
        json.dump(new_data, f, ensure_ascii=False, indent=2)
    logging.info("Database aggiornato")
    return load_database(db_path)