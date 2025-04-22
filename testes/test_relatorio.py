import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()


def test_gerar_relatorio(client):
    response = client.get('/relatorio_predicoes')
    assert response.status_code == 200
    data = response.get_json()
    assert "message" in data
    assert "file" in data
    assert data["file"].endswith(".csv")

def test_download_relatorio(client):
    response = client.get('/download_relatorio')
    assert response.status_code == 200
    assert response.headers['Content-Disposition'].startswith("attachment")
