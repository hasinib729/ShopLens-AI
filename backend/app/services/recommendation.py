import random
import numpy as np
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.database import models
from app.services.cold_start import ColdStartService
from app.services.embeddings import EmbeddingsService
from app.services.search import search_engine

class RecommendationService:
    @staticmethod
    def get_user_history_products(db: Session, session_id: str, user_id: Optional[int] = None) -> List[models.Product]:
        """Retrieves list of products that the user has interacted with (views, clicks)."""
        query = db.query(models.Product).join(
            models.UserActivity, models.UserActivity.product_id == models.Product.id
        )
        if user_id:
            query = query.filter(models.UserActivity.user_id == user_id)
        else:
            query = query.filter(models.UserActivity.session_id == session_id)
            
        # Get last 10 products
        activities = query.order_by(models.UserActivity.created_at.desc()).limit(10).all()
        return activities

    @classmethod
    def get_personalized_recommendations(cls, 
                                           db: Session, 
                                           session_id: str, 
                                           user_id: Optional[int] = None, 
                                           limit: int = 10) -> List[Dict[str, Any]]:
        """
        Calculates personalized recommendations.
        Uses a simulated Two-Tower Architecture:
        - User Tower: Aggregates embeddings of products in the user's history.
        - Product Tower: Retrieved using FAISS index lookups on the User Vector.
        """
        history_products = cls.get_user_history_products(db, session_id, user_id)
        
        # Cold start check
        if not history_products:
            return ColdStartService.get_recommendations_for_new_user(db, limit)
            
        # 1. Compile User Tower Representation Vector (768-D)
        user_vectors = []
        for p in history_products:
            text_str = f"{p.title} {p.description or ''} {p.brand or ''} {p.category or ''}"
            p_vec = EmbeddingsService.get_text_embedding(text_str)
            user_vectors.append(p_vec)
            
        # Average embeddings to form the User Vector
        user_vector = np.mean(user_vectors, axis=0)
        # Normalize
        user_vector = user_vector / np.linalg.norm(user_vector)
        
        # 2. Query Product Tower (FAISS Index search on User Vector)
        candidates = search_engine.vector_search(user_vector.tolist(), "text", limit * 3)
        
        # Filter out products already in history
        history_ids = {p.id for p in history_products}
        recommendations = []
        
        for p_id, score in candidates:
            if p_id in history_ids:
                continue
                
            product = db.query(models.Product).filter(models.Product.id == p_id).first()
            if product:
                # Find which product from history triggered this match (explainability)
                matching_hist_p = history_products[0]  # default to last viewed
                for hp in history_products:
                    if hp.category == product.category:
                        matching_hist_p = hp
                        break
                        
                explanation = f"Recommended because you viewed '{matching_hist_p.title}'"
                
                # Adjust score to percentage
                pct_score = round(max(0.1, score) * 100.0, 1)
                explanation_str = f"{explanation} (Match: {pct_score}%)"
                
                recommendations.append({
                    "product": product,
                    "score": score,
                    "explanation": explanation_str
                })
                
        # If not enough items, pad with popular items
        if len(recommendations) < limit:
            popular_items = ColdStartService.get_popular_products(db, limit)
            for p in popular_items:
                if p.id not in history_ids and p.id not in {r["product"].id for r in recommendations}:
                    recommendations.append({
                        "product": p,
                        "score": 0.5,
                        "explanation": "Recommended based on overall catalog popularity"
                    })
                    if len(recommendations) >= limit:
                        break
                        
        # Sort recommendations by score descending
        recommendations = sorted(recommendations, key=lambda x: x["score"], reverse=True)
        return recommendations[:limit]
        
    @classmethod
    def get_similar_products(cls, db: Session, product_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Retrieves similar products for the Product Details page using:
        Retrieval-Augmented Recommendations (Retrieval + Ranking).
        """
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            return []
            
        # 1. Retrieve visually similar candidates using CLIP
        img_vec = EmbeddingsService.get_image_embedding(product.image_url or product.title)
        candidates = search_engine.vector_search(img_vec, "image", limit * 3)
        
        similar_list = []
        for p_id, score in candidates:
            if p_id == product.id:
                continue
                
            p = db.query(models.Product).filter(models.Product.id == p_id).first()
            if p:
                sim_pct = round(max(0.1, score) * 100.0, 1)
                similar_list.append({
                    "product": p,
                    "score": score,
                    "explanation": f"Recommended because of {sim_pct}% visual similarity"
                })
                
        # Fallback to category overlap if no candidates found
        if not similar_list:
            matches = db.query(models.Product).filter(
                models.Product.id != product.id,
                models.Product.category == product.category
            ).limit(limit).all()
            for p in matches:
                similar_list.append({
                    "product": p,
                    "score": 0.7,
                    "explanation": "Recommended because it is in the same category"
                })
                
        return similar_list[:limit]
stream_recommender = RecommendationService()
