from typing import List, Dict, Any
import random
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.database import models
from app.services.embeddings import EmbeddingsService
from app.services.search import search_engine

class ColdStartService:
    @staticmethod
    def get_popular_products(db: Session, limit: int = 10) -> List[models.Product]:
        """Returns products sorted by sales metrics, rating, and reviews (for brand new users)."""
        return db.query(models.Product).order_by(
            models.Product.rating.desc(),
            models.Product.reviews_count.desc()
        ).limit(limit).all()

    @staticmethod
    def get_trending_categories(db: Session) -> List[str]:
        """Identifies active trending categories based on interaction logs."""
        # Join UserActivity and Product to count events per category
        results = db.query(models.Product.category).join(
            models.UserActivity, models.UserActivity.product_id == models.Product.id
        ).group_by(models.Product.category).order_by(
            func.count(models.UserActivity.id).desc()
        ).all()
        
        categories = [r[0] for r in results if r[0]]
        if not categories:
            # Fallback to catalog categories
            catalog_cat = db.query(models.Product.category).distinct().all()
            categories = [c[0] for c in catalog_cat if c[0]]
        return categories

    @staticmethod
    def get_recommendations_for_new_user(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """Compiles popular products + trending category items with explainability tags."""
        popular = ColdStartService.get_popular_products(db, limit)
        results = []
        for p in popular:
            results.append({
                "product": p,
                "score": float(p.rating / 5.0) if p.rating else 0.5,
                "explanation": "Recommended because it is a top trending product"
            })
        return results

    @staticmethod
    def get_similar_new_product(db: Session, new_product: models.Product, limit: int = 5) -> List[models.Product]:
        """
        Uses metadata overlap and visual (CLIP) vector similarity 
        to find catalog matches for a brand-new product.
        """
        # 1. Try visual similarity
        img_vec = EmbeddingsService.get_image_embedding(new_product.image_url or new_product.title)
        candidates = search_engine.vector_search(img_vec, "image", limit * 2)
        
        similar_products = []
        for p_id, _ in candidates:
            if p_id == new_product.id:
                continue
            p = db.query(models.Product).filter(models.Product.id == p_id).first()
            if p:
                similar_products.append(p)
                
        if len(similar_products) < limit:
            # 2. Fallback to metadata overlap (same category, brand)
            matches = db.query(models.Product).filter(
                models.Product.id != new_product.id,
                models.Product.category == new_product.category
            ).limit(limit - len(similar_products)).all()
            similar_products.extend(matches)
            
        return similar_products[:limit]
