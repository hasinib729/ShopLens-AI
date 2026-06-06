from app.database.db import SessionLocal
from app.database import models

def clean_database_products():
    print("Initializing database cleaning and deduplication...")
    db = SessionLocal()
    try:
        products = db.query(models.Product).all()
        cleaned_count = 0
        deleted_count = 0
        
        seen_titles = set()
        for p in products:
            # 1. Deduplication based on title
            if p.title in seen_titles:
                db.delete(p)
                deleted_count += 1
                continue
            seen_titles.add(p.title)
            
            # 2. Text normalization
            changed = False
            if p.description:
                trimmed = p.description.strip()
                if trimmed != p.description:
                    p.description = trimmed
                    changed = True
                    
            if p.brand:
                trimmed = p.brand.strip()
                if trimmed != p.brand:
                    p.brand = trimmed
                    changed = True
                    
            if changed:
                cleaned_count += 1
                
        db.commit()
        print(f"Cleaning completed. Cleaned: {cleaned_count} items. Deleted duplicates: {deleted_count} items.")
    finally:
        db.close()

if __name__ == "__main__":
    clean_database_products()
