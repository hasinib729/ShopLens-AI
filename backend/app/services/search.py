import os
import numpy as np
from typing import List, Dict, Any, Tuple
from sqlalchemy.orm import Session
from app.utils.config import settings
from app.database import models
from app.services.embeddings import EmbeddingsService

# Try loading FAISS
FAISS_AVAILABLE = False
try:
    import faiss
    FAISS_AVAILABLE = True
except ImportError:
    pass

class NumPyVectorIndex:
    """NumPy-based Flat Inner Product vector index (equivalent to FAISS FlatIP fallback)."""
    def __init__(self, dimension: int):
        self.dimension = dimension
        self.vectors = []
        self.ids = []

    def add(self, vectors: np.ndarray, ids: List[int]):
        for vec, idx in zip(vectors, ids):
            # Normalize vector to ensure cosine similarity
            norm = np.linalg.norm(vec)
            norm_vec = vec / norm if norm > 0 else vec
            self.vectors.append(norm_vec)
            self.ids.append(idx)

    def search(self, query_vector: np.ndarray, k: int) -> Tuple[np.ndarray, np.ndarray]:
        if not self.vectors:
            return np.array([[]]), np.array([[]])
            
        # Normalize query
        q_norm = np.linalg.norm(query_vector)
        q_vec = query_vector / q_norm if q_norm > 0 else query_vector
        
        # Calculate dot products
        vec_matrix = np.array(self.vectors)
        similarities = np.dot(vec_matrix, q_vec)
        
        # Sort indices descending
        top_k_indices = np.argsort(similarities)[::-1][:k]
        
        scores = similarities[top_k_indices]
        ids = np.array([self.ids[i] for i in top_k_indices])
        
        # Return format matches FAISS [distances, indices]
        return np.array([scores]), np.array([ids])

    def save(self, file_path: str):
        np.savez(file_path, vectors=np.array(self.vectors), ids=np.array(self.ids))

    def load(self, file_path: str):
        if os.path.exists(file_path):
            data = np.load(file_path)
            self.vectors = list(data["vectors"])
            self.ids = list(data["ids"])

class ShopLensSearchEngine:
    def __init__(self):
        self.text_index_path = os.path.join(settings.LOCAL_STORAGE_DIR, "models", "text_index.npz")
        self.image_index_path = os.path.join(settings.LOCAL_STORAGE_DIR, "models", "image_index.npz")
        
        # Initialize text index (768-D) and image index (512-D)
        if FAISS_AVAILABLE and settings.ACTIVE_MODE == "production":
            # Real FAISS Flat Inner Product
            self.text_index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
            self.image_index = faiss.IndexIDMap(faiss.IndexFlatIP(512))
        else:
            self.text_index = NumPyVectorIndex(768)
            self.image_index = NumPyVectorIndex(512)
            
        self.load_indexes()

    def load_indexes(self):
        """Loads serialized indexes from storage folder."""
        try:
            if FAISS_AVAILABLE and settings.ACTIVE_MODE == "production":
                text_path = self.text_index_path.replace(".npz", ".faiss")
                img_path = self.image_index_path.replace(".npz", ".faiss")
                if os.path.exists(text_path):
                    self.text_index = faiss.read_index(text_path)
                if os.path.exists(img_path):
                    self.image_index = faiss.read_index(img_path)
            else:
                self.text_index.load(self.text_index_path)
                self.image_index.load(self.image_index_path)
        except Exception as e:
            print(f"Error loading vector search indexes: {e}. Index might be empty.")

    def save_indexes(self):
        """Saves current state of indexes to disk."""
        try:
            if FAISS_AVAILABLE and settings.ACTIVE_MODE == "production":
                text_path = self.text_index_path.replace(".npz", ".faiss")
                img_path = self.image_index_path.replace(".npz", ".faiss")
                faiss.write_index(self.text_index, text_path)
                faiss.write_index(self.image_index, img_path)
            else:
                self.text_index.save(self.text_index_path)
                self.image_index.save(self.image_index_path)
        except Exception as e:
            print(f"Error saving indexes: {e}")

    def rebuild_indexes_from_db(self, db: Session):
        """Pipes DB catalog to rebuild both search index systems."""
        products = db.query(models.Product).all()
        if not products:
            return
            
        text_vectors = []
        image_vectors = []
        product_ids = []
        
        for p in products:
            # Generate text vector
            text_str = f"{p.title} {p.description or ''} {p.brand or ''} {p.category or ''}"
            text_vec = EmbeddingsService.get_text_embedding(text_str)
            text_vectors.append(text_vec)
            
            # Generate image vector (mock or real path)
            img_vec = EmbeddingsService.get_image_embedding(p.image_url or p.title)
            image_vectors.append(img_vec)
            
            product_ids.append(p.id)
            
        # Re-initialize indexes to clear old data
        if FAISS_AVAILABLE and settings.ACTIVE_MODE == "production":
            self.text_index = faiss.IndexIDMap(faiss.IndexFlatIP(768))
            self.image_index = faiss.IndexIDMap(faiss.IndexFlatIP(512))
            
            self.text_index.add_with_ids(np.array(text_vectors).astype("float32"), np.array(product_ids))
            self.image_index.add_with_ids(np.array(image_vectors).astype("float32"), np.array(product_ids))
        else:
            self.text_index = NumPyVectorIndex(768)
            self.image_index = NumPyVectorIndex(512)
            
            self.text_index.add(np.array(text_vectors), product_ids)
            self.image_index.add(np.array(image_vectors), product_ids)
            
        self.save_indexes()

    def vector_search(self, query_vector: List[float], index_type: str = "text", k: int = 50) -> List[Tuple[int, float]]:
        """Performs index search and returns a list of (product_db_id, similarity_score)."""
        q_arr = np.array(query_vector).astype("float32").reshape(1, -1)
        
        index = self.text_index if index_type == "text" else self.image_index
        
        if FAISS_AVAILABLE and settings.ACTIVE_MODE == "production":
            distances, indices = index.search(q_arr, k)
        else:
            distances, indices = index.search(q_arr[0], k)
            
        results = []
        if len(distances) > 0 and len(indices) > 0:
            for dist, idx in zip(distances[0], indices[0]):
                if idx != -1:  # FAISS padding index is -1
                    results.append((int(idx), float(dist)))
        return results

    def hybrid_search(self, text_vector: List[float], image_vector: List[float], text_weight: float = 0.5, k: int = 50) -> List[Tuple[int, float]]:
        """Performs late-fusion scoring combining text and visual search maps."""
        text_results = self.vector_search(text_vector, "text", k * 2)
        image_results = self.vector_search(image_vector, "image", k * 2)
        
        # Merge scores
        merged_scores = {}
        for p_id, score in text_results:
            merged_scores[p_id] = merged_scores.get(p_id, 0.0) + text_weight * score
            
        for p_id, score in image_results:
            merged_scores[p_id] = merged_scores.get(p_id, 0.0) + (1.0 - text_weight) * score
            
        # Sort merged scores descending
        sorted_results = sorted(merged_scores.items(), key=lambda item: item[1], reverse=True)
        return sorted_results[:k]

search_engine = ShopLensSearchEngine()
