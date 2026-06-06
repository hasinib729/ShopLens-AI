from app.services.embeddings import EmbeddingsService

def test_text_embedding_dimensions():
    vec = EmbeddingsService.get_text_embedding("running shoes")
    assert len(vec) == 768
    # Test normalization
    norm = sum(x*x for x in vec)
    assert abs(norm - 1.0) < 1e-4

def test_image_embedding_dimensions():
    vec = EmbeddingsService.get_image_embedding("mock_image.jpg")
    assert len(vec) == 512
    norm = sum(x*x for x in vec)
    assert abs(norm - 1.0) < 1e-4

def test_embeddings_fusion():
    t_vec = EmbeddingsService.get_text_embedding("red shoes")
    i_vec = EmbeddingsService.get_image_embedding("red_sneaker.jpg")
    f_vec = EmbeddingsService.fuse_embeddings(t_vec, i_vec, text_weight=0.6)
    assert len(f_vec) == 512
    norm = sum(x*x for x in f_vec)
    assert abs(norm - 1.0) < 1e-4
