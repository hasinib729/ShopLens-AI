import os
import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.utils.config import settings
from app.database import models
from app.feature_store.online_store import online_store

# Try loading XGBoost
XGBOOST_AVAILABLE = False
_xgb_model = None

try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    pass

class LTRRankerService:
    def __init__(self):
        self.model_path = os.path.join(settings.LOCAL_STORAGE_DIR, "models", "xgboost_ltr.json")
        self.load_model()

    def load_model(self):
        """Loads trained XGBoost Ranker model if available."""
        global _xgb_model
        if XGBOOST_AVAILABLE and os.path.exists(self.model_path):
            try:
                _xgb_model = xgb.Booster()
                _xgb_model.load_model(self.model_path)
            except Exception as e:
                print(f"Error loading XGBoost Ranker model: {e}")
                _xgb_model = None

    def score_candidate(self, 
                        p: models.Product, 
                        p_features: Dict[str, Any],
                        text_sim: float, 
                        image_sim: float,
                        parsed_query: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
        """
        Calculates a ranking score for a single candidate product.
        Returns the final score and a dictionary representing explainable feature contributions.
        """
        # 1. Feature Engineering
        brand_match = 1.0 if (parsed_query.get("brand") and p.brand and parsed_query["brand"].lower() == p.brand.lower()) else 0.0
        category_match = 1.0 if (parsed_query.get("category") and p.category and parsed_query["category"].lower() == p.category.lower()) else 0.0
        
        # Price match penalty (1.0 if within max_price budget, decreases as it goes over budget)
        price_diff_penalty = 1.0
        max_price = parsed_query.get("max_price")
        if max_price:
            if p.price <= max_price:
                price_diff_penalty = 1.0
            else:
                # Penalty based on how much it exceeds the max price
                pct_over = (p.price - max_price) / max_price
                price_diff_penalty = max(0.0, 1.0 - pct_over)
                
        rating_score = (p.rating / 5.0) if p.rating else 0.0
        
        sales_velocity = p_features.get("product_sales_velocity", 0)
        popularity_score = min(1.0, sales_velocity / 100.0) # Cap popularity at 100 purchases
        
        ctr = p_features.get("product_ctr", 0.0)
        
        # 2. Score calculation
        if XGBOOST_AVAILABLE and _xgb_model is not None:
            # Prepare feature vector matching LTR features order
            feature_vector = np.array([[
                text_sim,
                image_sim,
                brand_match,
                category_match,
                price_diff_penalty,
                rating_score,
                popularity_score,
                ctr
            ]])
            dmatrix = xgb.DMatrix(feature_vector)
            score = float(_xgb_model.predict(dmatrix)[0])
            
            # Simulated SHAP/feature contribution values for explainability
            contributions = {
                "Text Similarity": max(0.01, text_sim * 0.4),
                "Image Similarity": max(0.01, image_sim * 0.3),
                "Rating Score": max(0.01, rating_score * 0.15),
                "Popularity": max(0.01, popularity_score * 0.15)
            }
        else:
            # Fallback Local Heuristic LTR scoring formula (simulates GBDT ranker)
            contributions = {
                "Text Similarity": text_sim * 0.4,
                "Image Similarity": image_sim * 0.3,
                "Rating Score": rating_score * 0.15,
                "Popularity": popularity_score * 0.15
            }
            # Add match boosts
            boost = (brand_match * 0.3) + (category_match * 0.2) + (price_diff_penalty * 0.3)
            base_score = sum(contributions.values())
            score = base_score * (1.0 + boost)
            
        # Normalize contributions to percentages
        total_contrib = sum(contributions.values())
        if total_contrib > 0:
            contributions = {k: round((v / total_contrib) * 100.0, 1) for k, v in contributions.items()}
        else:
            contributions = {"Text Similarity": 40.0, "Image Similarity": 30.0, "Rating Score": 15.0, "Popularity": 15.0}
            
        return score, contributions

    def rank_products(self, 
                      db: Session, 
                      candidates: List[Tuple[int, float]], 
                      search_type: str,
                      parsed_query: Dict[str, Any],
                      limit: int = 20) -> List[Dict[str, Any]]:
        """
        Takes FAISS candidates (db_id, raw_similarity), engineers features, 
        evaluates LTR ranking model, and returns ranked products with explainability weights.
        """
        ranked_list = []
        for p_db_id, raw_sim in candidates:
            product = db.query(models.Product).filter(models.Product.id == p_db_id).first()
            if not product:
                continue
                
            p_features = online_store.get_product_features(db, p_db_id)
            
            # Map raw similarity based on search type
            text_sim = raw_sim if search_type == "text" else 0.5
            image_sim = raw_sim if search_type == "image" else (raw_sim if search_type == "hybrid" else 0.5)
            
            score, contributions = self.score_candidate(
                p=product,
                p_features=p_features,
                text_sim=text_sim,
                image_sim=image_sim,
                parsed_query=parsed_query
            )
            
            ranked_list.append({
                "product": product,
                "relevance_score": raw_sim,
                "final_rank_score": score,
                "feature_contributions": contributions
            })
            
        # Sort descending by final rank score
        ranked_list = sorted(ranked_list, key=lambda x: x["final_rank_score"], reverse=True)
        return ranked_list[:limit]

ltr_ranker = LTRRankerService()
