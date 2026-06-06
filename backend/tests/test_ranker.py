from app.services.ranking import ltr_ranker
from app.database import models

def test_ltr_ranking_contributions():
    product = models.Product(
        product_id="TEST001",
        title="Nike Test Shoe",
        price=3500.0,
        rating=4.5,
        brand="Nike",
        category="running shoes"
    )
    
    parsed_query = {
        "brand": "Nike",
        "category": "running shoes",
        "max_price": 5000.0
    }
    
    score, contributions = ltr_ranker.score_candidate(
        p=product,
        p_features={"product_sales_velocity": 10, "product_ctr": 0.1},
        text_sim=0.8,
        image_sim=0.7,
        parsed_query=parsed_query
    )
    
    assert score > 0.0
    assert "Text Similarity" in contributions
    assert "Image Similarity" in contributions
    assert abs(sum(contributions.values()) - 100.0) < 1.0  # Sum of contributions should be 100%
