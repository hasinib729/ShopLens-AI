from sqlalchemy.orm import Session
from app.database.db import SessionLocal
from app.services.recommendation import RecommendationService
from app.services.cold_start import ColdStartService
from app.utils.data_generator import seed_database

def test_recommendation_cold_start():
    db = SessionLocal()
    try:
        # Seed database to populate products
        seed_database(db)
        # User without history gets cold start results
        recs = RecommendationService.get_personalized_recommendations(
            db=db,
            session_id="session_new_user_123",
            user_id=None,
            limit=5
        )
        assert len(recs) > 0
        assert "trending" in recs[0]["explanation"] or "popularity" in recs[0]["explanation"]
    finally:
        db.close()

def test_trending_categories():
    db = SessionLocal()
    try:
        seed_database(db)
        cats = ColdStartService.get_trending_categories(db)
        assert len(cats) > 0
    finally:
        db.close()
