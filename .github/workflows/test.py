import json
import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
from main import app, get_db
from database import Base, engine, SessionLocal
from weaviate_client import setup_weaviate_schema, hybrid_search, add_prompt

# 設置測試數據庫
Base.metadata.create_all(bind=engine)
TestingSessionLocal = SessionLocal

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(scope="module")
def mock_weaviate():
    with patch("weaviate_client.client") as mock_client:
        yield mock_client

@pytest.fixture(scope="module")
def mock_llama():
    with patch("main.model") as mock_model, patch("main.tokenizer") as mock_tokenizer:
        mock_model.generate.return_value = [0]  # 模擬生成的token
        mock_tokenizer.decode.return_value = "這是一個測試回應"
        yield mock_model, mock_tokenizer

def test_setup_weaviate_schema(mock_weaviate):
    setup_weaviate_schema()
    mock_weaviate.schema.create.assert_called_once()

def test_hybrid_search(mock_weaviate):
    mock_weaviate.query.get.return_value.with_near_text.return_value.with_limit.return_value.do.return_value = {
        "data": {
            "Get": {
                "Prompt": [
                    {"content": "測試內容1"},
                    {"content": "測試內容2"}
                ]
            }
        }
    }
    results = hybrid_search("測試搜索")
    assert len(results["data"]["Get"]["Prompt"]) == 2

def test_query_rag_system(mock_weaviate, mock_llama):
    response = client.post("/query", json={"prompt": "測試查詢"})
    assert response.status_code == 200
    assert "response" in response.json()
    assert "model_version" in response.json()

def test_search_prompts():
    # 首先添加一些測試數據
    client.post("/query", json={"prompt": "測試查詢1"})
    client.post("/query", json={"prompt": "測試查詢2"})
    
    response = client.get("/prompts/search?query=測試")
    assert response.status_code == 200
    assert len(response.json()) > 0

def test_submit_feedback():
    # 首先創建一個響應
    query_response = client.post("/query", json={"prompt": "測試反饋"})
    response_id = query_response.json()["response_id"]
    
    feedback_data = {
        "response_id": response_id,
        "user_rating": 5,
        "comments": "很好的回答"
    }
    response = client.post("/feedback", json=feedback_data)
    assert response.status_code == 200
    assert response.json()["message"] == "反饋提交成功。"

def test_add_prompt(mock_weaviate):
    result = add_prompt("新的測試提示", "測試類別")
    mock_weaviate.data_object.create.assert_called_once()
    assert "id" in result

if __name__ == "__main__":
    pytest.main(["-v", "test_main.py"])
