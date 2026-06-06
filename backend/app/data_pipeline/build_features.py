from app.database.db import SessionLocal
from app.database import models
from app.feature_store.online_store import online_store

def compile_online_features():
    print("Compiling features for Feature Store caching...")
    db = SessionLocal()
    try:
        products = db.query(models.Product).all()
        for p in products:
            # Querying forces computation and updates cache in online store
            online_store.get_product_features(db, p.id)
            
        users = db.query(models.User).all()
        for u in users:
            online_store.get_user_features(db, u.id)
            
        print(f"Feature caching completed. Cached features for {len(products)} products and {len(users)} users.")
    finally:
        db.close()

if __name__ == "__main__":
    compile_online_features()
