import numpy as np
from typing import List, Set

class MLMetricsCalculator:
    @staticmethod
    def precision_at_k(recommended_ids: List[int], ground_truth_ids: Set[int], k: int) -> float:
        """Calculates Precision@K."""
        if not recommended_ids or not ground_truth_ids or k <= 0:
            return 0.0
        top_k = recommended_ids[:k]
        hits = sum(1 for idx in top_k if idx in ground_truth_ids)
        return hits / k

    @staticmethod
    def recall_at_k(recommended_ids: List[int], ground_truth_ids: Set[int], k: int) -> float:
        """Calculates Recall@K."""
        if not recommended_ids or not ground_truth_ids or k <= 0:
            return 0.0
        top_k = recommended_ids[:k]
        hits = sum(1 for idx in top_k if idx in ground_truth_ids)
        return hits / len(ground_truth_ids)

    @staticmethod
    def mrr(recommended_ids: List[int], ground_truth_ids: Set[int]) -> float:
        """Calculates Mean Reciprocal Rank."""
        if not recommended_ids or not ground_truth_ids:
            return 0.0
        for rank, idx in enumerate(recommended_ids, start=1):
            if idx in ground_truth_ids:
                return 1.0 / rank
        return 0.0

    @staticmethod
    def ndcg_at_k(recommended_ids: List[int], ground_truth_ids: Set[int], k: int) -> float:
        """Calculates Normalized Discounted Cumulative Gain @ K."""
        if not recommended_ids or not ground_truth_ids or k <= 0:
            return 0.0
            
        top_k = recommended_ids[:k]
        dcg = 0.0
        for rank, idx in enumerate(top_k, start=1):
            if idx in ground_truth_ids:
                dcg += 1.0 / np.log2(rank + 1)
                
        # Calculate Ideal DCG (IDCG)
        idcg = 0.0
        ideal_hits = min(len(ground_truth_ids), k)
        for rank in range(1, ideal_hits + 1):
            idcg += 1.0 / np.log2(rank + 1)
            
        if idcg == 0.0:
            return 0.0
        return dcg / idcg

    @staticmethod
    def average_precision(recommended_ids: List[int], ground_truth_ids: Set[int]) -> float:
        """Calculates Average Precision (AP) for MAP calculations."""
        if not recommended_ids or not ground_truth_ids:
            return 0.0
            
        ap = 0.0
        hits = 0
        for rank, idx in enumerate(recommended_ids, start=1):
            if idx in ground_truth_ids:
                hits += 1
                ap += hits / rank
                
        return ap / len(ground_truth_ids)

    @staticmethod
    def hit_rate_at_k(recommended_ids: List[int], target_id: int, k: int) -> float:
        """Calculates Hit Rate @ K (checks if target product is within top K recommendations)."""
        if not recommended_ids or k <= 0:
            return 0.0
        return 1.0 if target_id in recommended_ids[:k] else 0.0
