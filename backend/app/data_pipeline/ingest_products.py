import os
from app.database.db import SessionLocal
from app.utils.data_generator import seed_database

def run_ingestion():
    print("Initializing product ingestion pipeline...")
    db = SessionLocal()
    try:
        # Seeding serves as our robust default ingestion pipeline
        seed_database(db)
        print("Ingestion pipeline successfully completed. Catalog products loaded.")
    finally:
        db.close()

if __name__ == "__main__":
    run_ingestion()
