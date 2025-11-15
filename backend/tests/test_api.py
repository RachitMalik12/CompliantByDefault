import pytest
from httpx import AsyncClient
from backend.src.api import app

@pytest.mark.asyncio
async def test_health_check():
    """Test health check endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"

@pytest.mark.asyncio
async def test_root_endpoint():
    """Test root endpoint."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/")
    
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data

@pytest.mark.asyncio
async def test_scan_local_invalid_path():
    """Test local scan with invalid path."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/scan/local",
            json={"path": "/nonexistent/path"}
        )
    
    assert response.status_code == 400

@pytest.mark.asyncio
async def test_scan_github_invalid_url():
    """Test GitHub scan with invalid URL."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post(
            "/scan/github",
            json={"repo_url": "not-a-valid-url"}
        )
    
    # Should return error for invalid URL
    assert response.status_code in [400, 500]

@pytest.mark.asyncio
async def test_get_nonexistent_report():
    """Test getting a report that doesn't exist."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/report/nonexistent-id")
    
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_list_reports():
    """Test listing reports."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/reports")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)

@pytest.mark.asyncio
async def test_get_controls():
    """Test getting SOC2 controls."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/controls")
    
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    # Should have control IDs like CC1, CC2, etc.
    assert any(key.startswith('CC') for key in data.keys())
