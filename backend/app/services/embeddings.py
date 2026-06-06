import numpy as np
import os
import hashlib
from typing import List, Union
from app.utils.config import settings

# Global models cache
_text_model = None
_clip_model = None
_clip_processor = None

def init_production_models():
    """Initializes heavy deep learning models if in production mode."""
    global _text_model, _clip_model, _clip_processor
    
    # Try importing deep learning packages
    try:
        import torch
        from sentence_transformers import SentenceTransformer
        from transformers import CLIPModel, CLIPProcessor
        
        print("Loading SentenceTransformer (all-mpnet-base-v2)...")
        # all-mpnet-base-v2 outputs 768-dimensional embeddings
        _text_model = SentenceTransformer("all-mpnet-base-v2")
        
        print("Loading CLIP (openai/clip-vit-base-patch32)...")
        # clip-vit-base-patch32 outputs 512-dimensional embeddings
        _clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
        _clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")
        
    except ImportError as e:
        print(f"Warning: Production ML libraries missing ({e}). Falling back to Local Inference Mode.")
        settings.ACTIVE_MODE = "local"

class EmbeddingsService:
    @staticmethod
    def get_text_embedding(text: str) -> List[float]:
        """
        Generates a 768-dimensional text embedding.
        In local mode, returns a deterministic hash-based vector.
        """
        if settings.ACTIVE_MODE == "production":
            if _text_model is None:
                init_production_models()
            if _text_model is not None:
                vector = _text_model.encode(text)
                return vector.tolist()
                
        # Fallback Local Inference Mode: Deterministic Hashing
        np.random.seed(int(hashlib.md5(text.encode("utf-8")).hexdigest(), 16) % (2**32 - 1))
        vector = np.random.randn(768)
        vector = vector / np.linalg.norm(vector)  # Normalize
        return vector.tolist()

    @staticmethod
    def get_image_embedding(image_path: str) -> List[float]:
        """
        Generates a 512-dimensional visual embedding.
        In local mode, returns a deterministic vector based on filename.
        """
        if settings.ACTIVE_MODE == "production":
            if _clip_model is None:
                init_production_models()
            if _clip_model is not None and os.path.exists(image_path):
                import torch
                from PIL import Image
                try:
                    image = Image.open(image_path).convert("RGB")
                    inputs = _clip_processor(images=image, return_tensors="pt")
                    with torch.no_grad():
                        image_features = _clip_model.get_image_features(**inputs)
                    # Normalize
                    image_features = image_features / image_features.norm(dim=-1, keepdim=True)
                    return image_features.flatten().tolist()
                except Exception as e:
                    print(f"Error processing image: {e}. Using fallback embedding.")
                    
        # Fallback Local Inference Mode: Hashing image path/filename
        filename = os.path.basename(image_path)
        np.random.seed(int(hashlib.md5(filename.encode("utf-8")).hexdigest(), 16) % (2**32 - 1))
        vector = np.random.randn(512)
        vector = vector / np.linalg.norm(vector)
        return vector.tolist()

    @classmethod
    def fuse_embeddings(cls, text_embedding: List[float], image_embedding: List[float], text_weight: float = 0.5) -> List[float]:
        """
        Performs early-fusion by combining text (768-D) and image (512-D) embeddings.
        To maintain vector search dimensions, we project or pad the fused vector to 512 dimensions.
        """
        # Concat projection or simple projection to 512
        # Project text embedding to 512
        text_arr = np.array(text_embedding)
        image_arr = np.array(image_embedding)
        
        # Project text down to 512 using simple deterministic slicing or interpolation
        if len(text_arr) == 768:
            # Simple downsampling to 512-D
            indices = np.linspace(0, len(text_arr) - 1, 512).astype(int)
            projected_text = text_arr[indices]
            # Normalize
            projected_text = projected_text / np.linalg.norm(projected_text)
        else:
            projected_text = text_arr
            
        # Weighted fusion
        fused = text_weight * projected_text + (1.0 - text_weight) * image_arr
        fused = fused / np.linalg.norm(fused)
        return fused.tolist()
