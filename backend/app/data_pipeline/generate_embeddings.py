from app.database.db import SessionLocal
from app.services.search import search_engine

def run_embeddings_pipeline():
    print("Generating product catalog text and visual embeddings...")
    db = SessionLocal()
    try:
        search_engine.rebuild_indexes_from_db(db)
        print("Embeddings generated and vector indices rebuilt successfully.")
    finally:
        db.close()

if __name__ == "__main__":
    run_embeddings_pipeline()
