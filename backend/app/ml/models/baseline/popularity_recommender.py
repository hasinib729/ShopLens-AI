from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.database import models

class PopularityRecommenderBaseline:
    @staticmethod
    def recommend(db: Session, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Recommends the most popular products in the catalog.
        Popularity is computed based on rating and reviews count.
        """
        products = db.query(models.Product).order_by(
            models.Product.rating.desc(),
            models.Product.reviews_count.desc()
        ).limit(limit).all()
        
        results = []
        for p in products:
            results.append({
                "product": p,
                "score": float(p.rating / 5.0) if p.rating else 0.5,
                "explanation": "Recommended based on overall catalog popularity"
            })
        return results
