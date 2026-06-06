import pandas as pd
import numpy as np
import random
from typing import Dict, Any
from sqlalchemy.orm import Session
from app.database import models
from app.feature_store.feature_registry import FeatureRegistry

class OfflineFeatureStore:
    @staticmethod
    def get_user_features(db: Session, user_id: int) -> Dict[str, Any]:
        """Compiles historical aggregates for a specific user."""
        # Calculate click count
        clicks = db.query(models.UserActivity).filter(
            models.UserActivity.user_id == user_id,
            models.UserActivity.event_type == "click"
        ).count()
        
        # Calculate purchases
        purchases = db.query(models.UserActivity).filter(
            models.UserActivity.user_id == user_id,
            models.UserActivity.event_type == "purchase"
        ).count()
        
        # Average dwell time
        views = db.query(models.UserActivity).filter(
            models.UserActivity.user_id == user_id,
            models.UserActivity.event_type == "view"
        ).all()
        avg_dwell = np.mean([v.dwell_time for v in views]) if views else 0.0
        
        # Top Category Preference
        activities = db.query(models.UserActivity, models.Product).join(
            models.Product, models.UserActivity.product_id == models.Product.id
        ).filter(models.UserActivity.user_id == user_id).all()
        
        categories = [p.category for _, p in activities if p.category]
        favorite_cat = max(set(categories), key=categories.count) if categories else None
        
        # Click through rate (clicks / views)
        view_count = len(views)
        ctr = clicks / view_count if view_count > 0 else 0.0
        
        return {
            "user_id": user_id,
            "user_click_count": clicks,
            "user_purchase_count": purchases,
            "user_avg_dwell_time": float(avg_dwell),
            "user_favorite_category": favorite_cat,
            "user_ctr": ctr
        }

    @staticmethod
    def get_product_features(db: Session, product_id: int) -> Dict[str, Any]:
        """Compiles historical aggregates for a specific product."""
        product = db.query(models.Product).filter(models.Product.id == product_id).first()
        if not product:
            return {}
            
        # Views
        views = db.query(models.UserActivity).filter(
            models.UserActivity.product_id == product_id,
            models.UserActivity.event_type == "view"
        ).count()
        
        # Clicks
        clicks = db.query(models.UserActivity).filter(
            models.UserActivity.product_id == product_id,
            models.UserActivity.event_type == "click"
        ).count()
        
        # Sales Velocity (purchases in database)
        sales = db.query(models.UserActivity).filter(
            models.UserActivity.product_id == product_id,
            models.UserActivity.event_type == "purchase"
        ).count()
        
        ctr = clicks / views if views > 0 else 0.0
        
        return {
            "product_id": product_id,
            "product_sales_velocity": sales,
            "product_view_count": views,
            "product_ctr": ctr,
            "product_price": product.price,
            "product_rating": product.rating,
            "product_reviews_count": product.reviews_count
        }

    @classmethod
    def compile_ltr_training_dataset(cls, db: Session) -> pd.DataFrame:
        """
        Compiles the historical dataset for LTR XGBoost training.
        Returns a Pandas DataFrame containing query-product pairs, features, and target labels.
        """
        logs = db.query(models.ABExperimentLog).all()
        if not logs:
            # Generate mock dataset for LTR training if no active logs exist
            records = []
            products = db.query(models.Product).all()
            for i in range(500):
                p = random.choice(products)
                sim = random.uniform(0.1, 0.95)
                # Label: 0 = view, 1 = click, 2 = purchase
                label = random.choices([0, 1, 2], weights=[0.7, 0.25, 0.05])[0]
                records.append({
                    "query_id": random.randint(1, 10),
                    "product_id": p.id,
                    "semantic_similarity": sim,
                    "visual_similarity": random.uniform(0.1, 0.9) if label > 0 else sim * 0.8,
                    "brand_match": random.choice([0, 1]),
                    "category_match": random.choice([0, 1]),
                    "price_distance": random.uniform(0, 5000),
                    "product_rating": p.rating,
                    "product_ctr": random.uniform(0.01, 0.3),
                    "product_sales_velocity": random.randint(0, 50),
                    "label": label
                })
            return pd.DataFrame(records)
            
        # Load real logs
        records = []
        for log in logs:
            p_features = cls.get_product_features(db, log.product_id)
            # Find semantic similarity between log.query_text and product title
            # In mock LTR, simulate similarity score
            text_sim = random.uniform(0.4, 0.95) if log.is_clicked else random.uniform(0.05, 0.5)
            img_sim = random.uniform(0.4, 0.95) if log.is_purchased else random.uniform(0.05, 0.5)
            
            # Label conversion: 2 if purchased, 1 if clicked, 0 otherwise
            label = 2 if log.is_purchased else (1 if log.is_clicked else 0)
            
            records.append({
                "query_id": log.experiment_name,  # group by experiment runs
                "product_id": log.product_id,
                "semantic_similarity": text_sim,
                "visual_similarity": img_sim,
                "brand_match": 1 if p_features.get("brand_match") else 0,
                "category_match": 1 if p_features.get("category_match") else 0,
                "price_distance": abs(p_features.get("product_price", 1000.0) - 3000.0), # distance to reference price
                "product_rating": p_features.get("product_rating", 4.0),
                "product_ctr": p_features.get("product_ctr", 0.05),
                "product_sales_velocity": p_features.get("product_sales_velocity", 5),
                "label": label
            })
        return pd.DataFrame(records)
