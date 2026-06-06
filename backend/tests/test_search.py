import numpy as np
from app.services.search import NumPyVectorIndex, ShopLensSearchEngine

def test_numpy_vector_index():
    index = NumPyVectorIndex(768)
    vec1 = np.random.randn(768)
    vec2 = np.random.randn(768)
    
    index.add(np.array([vec1, vec2]), [101, 102])
    
    # Search for first vector
    scores, ids = index.search(vec1, k=1)
    assert ids[0][0] == 101
    assert scores[0][0] > 0.9  # Normalized dot product should be close to 1

def test_search_engine_load():
    engine = ShopLensSearchEngine()
    assert engine.text_index is not None
    assert engine.image_index is not None
