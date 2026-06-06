import os
import json
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.utils.config import settings
from app.database import models
from app.services.query_understanding import QueryUnderstandingService

class RelevanceBenchmarkDataset:
    def __init__(self):
        self.benchmark_file = os.path.join(settings.LOCAL_STORAGE_DIR, "datasets", "relevance_benchmark.json")

    def generate_benchmark(self, db: Session) -> Dict[str, List[int]]:
        """
        Dynamically scans database catalog to compile query-to-product ground truth lists.
        Maps queries like 'red running shoes under 10000' to actual matching catalog IDs.
        """
        test_queries = [
            "red running shoes",
            "black running shoes",
            "Fossil handbags",
            "Apple smartwatch",
            "wireless gaming mouse",
            "blue formal shirts",
            "Logitech wireless mouse"
        ]
        
        benchmark = {}
        products = db.query(models.Product).all()
        
        for query in test_queries:
            # Parse attributes using query understanding
            parsed = QueryUnderstandingService.parse_query(query)
            cat = parsed.get("category")
            color = parsed.get("color")
            brand = parsed.get("brand")
            max_price = parsed.get("max_price")
            
            relevant_ids = []
            for p in products:
                # Assess relevance rules
                is_relevant = True
                
                if cat and (not p.category or cat.lower() != p.category.lower()):
                    is_relevant = False
                if color and (not p.features or p.features.get("color", "").lower() != color.lower()):
                    is_relevant = False
                if brand and (not p.brand or brand.lower() != p.brand.lower()):
                    is_relevant = False
                if max_price and p.price > max_price:
                    is_relevant = False
                    
                # Additional title-keyword match if no categories found
                if not cat and not color and not brand:
                    query_words = query.lower().split()
                    if not any(word in p.title.lower() for word in query_words):
                        is_relevant = False
                        
                if is_relevant:
                    relevant_ids.append(p.id)
                    
            # Only record if we found matching products in catalog
            if relevant_ids:
                benchmark[query] = relevant_ids
                
        # Save benchmark to file
        os.makedirs(os.path.dirname(self.benchmark_file), exist_ok=True)
        with open(self.benchmark_file, "w") as f:
            json.dump(benchmark, f, indent=2)
            
        print(f"Generated ground-truth relevance benchmark mapping {len(benchmark)} queries to {self.benchmark_file}")
        return benchmark

    def load_benchmark(self, db: Session) -> Dict[str, List[int]]:
        """Loads relevance benchmark from file. Generates it if missing."""
        if not os.path.exists(self.benchmark_file):
            return self.generate_benchmark(db)
            
        try:
            with open(self.benchmark_file, "r") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error reading benchmark file: {e}")
            return self.generate_benchmark(db)

relevance_benchmark = RelevanceBenchmarkDataset()
