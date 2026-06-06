from app.services.query_understanding import QueryUnderstandingService

def test_query_parsing_running_shoes():
    q = "red running shoes under 3000"
    result = QueryUnderstandingService.parse_query(q)
    assert result["category"] == "running shoes"
    assert result["color"] == "Red"
    assert result["max_price"] == 3000.0

def test_query_parsing_mouse():
    q = "Logitech wireless gaming mouse"
    result = QueryUnderstandingService.parse_query(q)
    assert result["category"] == "gaming mouse"
    assert result["brand"] == "Logitech"
    assert result["max_price"] is None

def test_query_parsing_shirt():
    q = "black formal shirt slim fit"
    result = QueryUnderstandingService.parse_query(q)
    assert result["category"] == "formal shirts"
    assert result["color"] == "Black"
