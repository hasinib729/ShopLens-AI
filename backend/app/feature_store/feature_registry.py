from typing import List, Dict, Any

class FeatureDefinition:
    def __init__(self, name: str, value_type: str, description: str):
        self.name = name
        self.value_type = value_type
        self.description = description

class FeatureRegistry:
    # User Feature Definitions
    USER_FEATURES: Dict[str, FeatureDefinition] = {
        "user_click_count": FeatureDefinition("user_click_count", "int", "Total clicks by user"),
        "user_purchase_count": FeatureDefinition("user_purchase_count", "int", "Total purchases by user"),
        "user_avg_dwell_time": FeatureDefinition("user_avg_dwell_time", "float", "Average dwell time of user in seconds"),
        "user_favorite_category": FeatureDefinition("user_favorite_category", "string", "Top category user interacts with"),
        "user_ctr": FeatureDefinition("user_ctr", "float", "Historical click-through rate of user")
    }

    # Product Feature Definitions
    PRODUCT_FEATURES: Dict[str, FeatureDefinition] = {
        "product_sales_velocity": FeatureDefinition("product_sales_velocity", "int", "Number of purchases in last 7 days"),
        "product_view_count": FeatureDefinition("product_view_count", "int", "Total views count"),
        "product_ctr": FeatureDefinition("product_ctr", "float", "Product click-through rate"),
        "product_price": FeatureDefinition("product_price", "float", "Price of product"),
        "product_rating": FeatureDefinition("product_rating", "float", "Rating score"),
        "product_reviews_count": FeatureDefinition("product_reviews_count", "int", "Total reviews count")
    }

    # Ranking Feature Definitions
    RANKING_FEATURES: List[str] = [
        "semantic_similarity",
        "visual_similarity",
        "brand_match",
        "category_match",
        "price_distance",
        "product_rating",
        "product_ctr",
        "product_sales_velocity"
    ]
