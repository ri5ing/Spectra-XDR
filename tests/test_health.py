"""Unit and integration tests for root and health check endpoints."""

from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)


def test_root_endpoint():
    """Verify GET / returns 200 OK, JSON format, and app name SPECTRA-XDR."""
    response = client.get("/")
    assert response.status_code == 200
    
    data = response.json()
    assert data["app"] == "SPECTRA-XDR"
    assert data["status"] == "running"
    assert "version" in data


def test_health_endpoint():
    """Verify GET /health returns 200 OK, JSON format, and healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["app"] == "SPECTRA-XDR"
    assert "environment" in data


def test_404_error_handling():
    """Verify unknown route returns standard HTTP error JSON response."""
    response = client.get("/nonexistent-route")
    assert response.status_code == 404
    data = response.json()
    assert "error" in data
    assert data["status_code"] == 404
