import pytest
import numpy as np
import os
import sys

# Ensure root folder is accessible for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import app, get_model
from src.train import generate_synthetic_housing_data

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client

def test_data_generation_quality():
    """Validates synthetic housing dataset dimensions and constraints"""
    df = generate_synthetic_housing_data(n_samples=100)
    assert len(df) == 100
    assert df.isnull().sum().sum() == 0, "Dataset contains null values"
    assert (df["area"] > 0).all(), "Area must be positive"
    assert (df["price"] > 0).all(), "Price must be strictly positive"

def test_model_loading_and_inference():
    """Ensures model artifact exists, loads cleanly, and gives valid prediction"""
    model, features = get_model()
    assert model is not None, "Model failed to load"
    assert len(features) == 5, f"Expected 5 features, got {len(features)}"

    # Benchmark test input: 2000 sqft, 3 BHK, 2 Bath, 2 Storey, 1 Car
    sample = np.array([[2000, 3, 2, 2, 1]])
    pred = model.predict(sample)
    assert pred[0] > 50000, f"Predicted price unrealistically low: {pred[0]}"
    assert pred[0] < 1000000, f"Predicted price unrealistically high: {pred[0]}"

def test_health_endpoint(client):
    """Verifies that the /health monitoring endpoint returns HTTP 200"""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "healthy"
    assert data["model_loaded"] is True

def test_api_predict_endpoint_success(client):
    """Verifies REST API inference endpoint /api/predict"""
    payload = {
        "area": 1850,
        "bedrooms": 3,
        "bathrooms": 2,
        "stories": 2,
        "parking": 1
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 200
    data = response.get_json()
    assert "estimated_price" in data
    assert data["estimated_price"] > 0
    assert data["currency"] == "USD"

def test_api_predict_invalid_input(client):
    """Verifies that negative or zero area returns HTTP 400 Bad Request"""
    payload = {
        "area": -500,
        "bedrooms": 2,
        "bathrooms": 1,
        "stories": 1,
        "parking": 0
    }
    response = client.post("/api/predict", json=payload)
    assert response.status_code == 400
    data = response.get_json()
    assert "error" in data

