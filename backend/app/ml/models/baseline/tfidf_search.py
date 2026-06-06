import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.database import models

# Try loading scikit-learn
SKLEARN_AVAILABLE = False
try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    SKLEARN_AVAILABLE = True
except ImportError:
    pass

class TFIDFSearchBaseline:
    def __init__(self):
        self.vectorizer = None
        self.tfidf_matrix = None
        self.product_ids = []
        
    def fit(self, products: List[models.Product]):
        """Fits TF-IDF vectorizer on product text corpuses."""
        if not products:
            return
            
        self.product_ids = [p.id for p in products]
        corpus = [f"{p.title} {p.description or ''} {p.brand or ''} {p.category or ''}" for p in products]
        
        if SKLEARN_AVAILABLE:
            try:
                self.vectorizer = TfidfVectorizer(stop_words="english")
                self.tfidf_matrix = self.vectorizer.fit_transform(corpus)
            except Exception as e:
                print(f"Error training TF-IDF: {e}")
                self.vectorizer = None
                
    def search(self, query: str, k: int = 50) -> List[Tuple[int, float]]:
        """Retrieves products using TF-IDF cosine similarity."""
        if not self.product_ids:
            return []
            
        if SKLEARN_AVAILABLE and self.vectorizer and self.tfidf_matrix is not None:
            try:
                query_vec = self.vectorizer.transform([query])
                similarities = cosine_similarity(self.tfidf_matrix, query_vec).flatten()
                
                # Sort indices descending
                top_k_indices = np.argsort(similarities)[::-1][:k]
                
                results = []
                for idx in top_k_indices:
                    score = float(similarities[idx])
                    if score > 0.0:  # Only return matching entries
                        results.append((self.product_ids[idx], score))
                return results
            except Exception as e:
                print(f"TF-IDF search error: {e}")
                
        # Basic keyword match fallback if sklearn is missing
        results = []
        query_words = query.lower().split()
        for idx in self.product_ids:
            # Simple mock score based on word intersection
            score = 0.5
            results.append((idx, score))
        return results[:k]
