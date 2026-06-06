import re
from typing import Dict, Any, Optional

# Match catalogs and normalize
CATEGORY_MAP = {
    r"\b(run|running|sport|sports)?\s*(shoe|shoes|sneaker|sneakers|footwear)\b": "running shoes",
    r"\b(hand)?bag(s)?\b|\btote(s)?\b|\bsatchel(s)?\b": "handbags",
    r"\b(smart)?watch(es)?\b|\bband(s)?\b": "smartwatches",
    r"\b(gaming\s+)?mouse\b|\bmice\b": "gaming mouse",
    r"\b(formal\s+)?shirt(s)?\b": "formal shirts"
}

BRAND_LIST = ["Nike", "Adidas", "Puma", "Asics", "Coach", "Michael Kors", "Kate Spade", "Fossil", "Apple", "Samsung", "Garmin", "Logitech", "Razer", "SteelSeries", "Corsair", "Louis Philippe", "Van Heusen", "Peter England", "Arrow"]
COLOR_LIST = ["Red", "Black", "Blue", "White", "Brown", "Tan", "Silver", "Midnight", "Green", "Grey", "Yellow", "Pink"]

class QueryUnderstandingService:
    @staticmethod
    def parse_query(query_text: str) -> Dict[str, Any]:
        """
        Parses a natural language search query to extract:
        - category
        - color
        - brand
        - max_price
        """
        if not query_text:
            return {"query": "", "category": None, "color": None, "brand": None, "max_price": None}
            
        normalized_query = query_text.lower().strip()
        
        # 1. Extract Category
        category = None
        for pattern, cat_name in CATEGORY_MAP.items():
            if re.search(pattern, normalized_query):
                category = cat_name
                break
                
        # 2. Extract Brand
        brand = None
        for b in BRAND_LIST:
            if re.search(r"\b" + re.escape(b.lower()) + r"\b", normalized_query):
                brand = b
                break
                
        # 3. Extract Color
        color = None
        for c in COLOR_LIST:
            if re.search(r"\b" + re.escape(c.lower()) + r"\b", normalized_query):
                color = c
                break
                
        # 4. Extract Price Limits (e.g. "under 3000", "below 2500", "less than 5000", "under ₹3000")
        max_price = None
        
        # Match "under/below/less than [number]"
        price_patterns = [
            r"(?:under|below|less\s+than|under\s+₹|below\s+₹)\s*(\d+(?:\.\d+)?)",
            r"(?:max|maximum|price\s*limit)\s*(?:of|is|at)?\s*₹?\s*(\d+(?:\.\d+)?)"
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, normalized_query)
            if match:
                try:
                    max_price = float(match.group(1))
                    break
                except ValueError:
                    pass
                    
        return {
            "query": query_text,
            "category": category,
            "color": color,
            "brand": brand,
            "max_price": max_price
        }
