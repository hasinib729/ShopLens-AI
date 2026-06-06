from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_api_search_text():
    response = client.post("/search/text", json={
        "query": "red running shoes under 5000",
        "session_id": "test_sess_api_1",
        "use_ranker": True
    })
    assert response.status_code == 200
    data = response.json()
    assert "results" in data
    assert "query_understanding" in data
    assert "latency_ms" in data

def test_api_recommendations():
    response = client.post("/recommendations", json={
        "session_id": "test_sess_api_1",
        "limit": 5
    })
    assert response.status_code == 200
    data = response.json()
    assert "recommendations" in data

def test_api_analytics_overview():
    response = client.get("/analytics/overview")
    assert response.status_code == 200
    data = response.json()
    assert "total_products" in data
    assert "active_users" in data
