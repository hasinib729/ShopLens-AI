import math
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.database import models

class BM25SearchBaseline:
    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.doc_len = []
        self.avg_doc_len = 0.0
        self.doc_count = 0
        self.product_ids = []
        self.vocab = {}
        # Maps word -> list of doc frequencies
        self.doc_freqs = {}
        # Maps doc_idx -> word -> freq
        self.term_freqs = []

    def fit(self, products: List[models.Product]):
        """Fits BM25 statistics on catalog descriptions."""
        if not products:
            return
            
        self.product_ids = [p.id for p in products]
        self.doc_count = len(products)
        
        self.term_freqs = []
        self.doc_len = []
        
        total_len = 0
        for p in products:
            text = f"{p.title} {p.description or ''} {p.brand or ''} {p.category or ''}"
            words = text.lower().split()
            self.doc_len.append(len(words))
            total_len += len(words)
            
            # Count terms
            freqs = {}
            for w in words:
                freqs[w] = freqs.get(w, 0) + 1
                
            self.term_freqs.append(freqs)
            
            # Update Document Frequency (DF)
            for w in freqs.keys():
                self.doc_freqs[w] = self.doc_freqs.get(w, 0) + 1
                
        self.avg_doc_len = total_len / self.doc_count if self.doc_count > 0 else 0.0

    def get_idf(self, word: str) -> float:
        """Calculates Inverse Document Frequency with smoothing."""
        df = self.doc_freqs.get(word, 0)
        # Standard BM25 IDF formula
        return math.log((self.doc_count - df + 0.5) / (df + 0.5) + 1.0)

    def search(self, query: str, k: int = 50) -> List[Tuple[int, float]]:
        """Scores catalog docs for BM25 relevance match."""
        if not self.product_ids or self.doc_count == 0:
            return []
            
        query_words = query.lower().split()
        scores = []
        
        for doc_idx, p_id in enumerate(self.product_ids):
            score = 0.0
            dl = self.doc_len[doc_idx]
            tf_dict = self.term_freqs[doc_idx]
            
            for w in query_words:
                if w in tf_dict:
                    tf = tf_dict[w]
                    idf = self.get_idf(w)
                    
                    # BM25 tf component
                    numerator = tf * (self.k1 + 1.0)
                    denominator = tf + self.k1 * (1.0 - self.b + self.b * (dl / self.avg_doc_len))
                    score += idf * (numerator / denominator)
            
            if score > 0.0:
                scores.append((p_id, score))
                
        # Sort descending
        scores = sorted(scores, key=lambda x: x[1], reverse=True)
        return scores[:k]
