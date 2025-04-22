import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    return app.test_client()

def test_predict_valido(client):
    payload = {
        "StudentID": 1,
        "Age": 17,
        "Gender": 0,
        "Ethnicity": 0,
        "ParentalEducation": 1,
        "StudyTimeWeekly": 5.5,
        "Absences": 3,
        "Tutoring": 1,
        "ParentalSupport": 2,
        "Extracurricular": 1,
        "Sports": 0,
        "Music": 1,
        "Volunteering": 0,
        "GPA": 8.0
    }

    response = client.post('/predict', json=payload)
    data = response.get_json()
    print(data)
    assert response.status_code == 200
    assert "GradeClass predito" in data
    assert isinstance(data["GradeClass predito"], int)

def test_predict_faltando_campo(client):
    payload = {
        "StudentID": 1,
        "Age": 17,
        "Gender": 0
    }

    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert "Campo obrigatório ausente" in response.get_json()["error"]

def test_pipeline_predicao_armazenada(client):
    payload = {
        "StudentID": 99,
        "Age": 18,
        "Gender": 1,
        "Ethnicity": 2,
        "ParentalEducation": 3,
        "StudyTimeWeekly": 6,
        "Absences": 2,
        "Tutoring": 0,
        "ParentalSupport": 1,
        "Extracurricular": 0,
        "Sports": 1,
        "Music": 0,
        "Volunteering": 1,
        "GPA": 7.5
    }

    client.post('/predict', json=payload)

    response = client.get('/predicoes')
    assert response.status_code == 200
    data = response.get_json()
    assert any(p['student_id'] == 99 for p in data)

# -------------------------
# Testes TC07 - Limites e valores inválidos
# -------------------------

def test_idade_abaixo_limite(client):
    payload = {
        "StudentID": 2,
        "Age": 4,
        "Gender": 0,
        "Ethnicity": 0,
        "ParentalEducation": 1,
        "StudyTimeWeekly": 6,
        "Absences": 0,
        "Tutoring": 0,
        "ParentalSupport": 1,
        "Extracurricular": 1,
        "Sports": 0,
        "Music": 1,
        "Volunteering": 1,
        "GPA": 7.0
    }

    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert "Idade fora dos limites" in response.get_json()["error"]

def test_idade_acima_limite(client):
    payload = {
        "StudentID": 3,
        "Age": 101,
        "Gender": 1,
        "Ethnicity": 1,
        "ParentalEducation": 2,
        "StudyTimeWeekly": 4,
        "Absences": 1,
        "Tutoring": 1,
        "ParentalSupport": 0,
        "Extracurricular": 1,
        "Sports": 1,
        "Music": 1,
        "Volunteering": 0,
        "GPA": 6.5
    }

    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert "Idade fora dos limites" in response.get_json()["error"]

def test_gpa_invalido(client):
    payload = {
        "StudentID": 4,
        "Age": 20,
        "Gender": 1,
        "Ethnicity": 1,
        "ParentalEducation": 2,
        "StudyTimeWeekly": 5,
        "Absences": 0,
        "Tutoring": 1,
        "ParentalSupport": 1,
        "Extracurricular": 0,
        "Sports": 0,
        "Music": 0,
        "Volunteering": 1,
        "GPA": 11.0
    }

    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert "GPA fora dos limites" in response.get_json()["error"]

def test_valores_booleans_invalidos(client):
    payload = {
        "StudentID": 5,
        "Age": 18,
        "Gender": 0,
        "Ethnicity": 1,
        "ParentalEducation": 3,
        "StudyTimeWeekly": 3,
        "Absences": 1,
        "Tutoring": 2,  # inválido
        "ParentalSupport": 0,
        "Extracurricular": 3,  # inválido
        "Sports": 0,
        "Music": 1,
        "Volunteering": 5,  # inválido
        "GPA": 8.5
    }

    response = client.post('/predict', json=payload)
    assert response.status_code == 400
    assert "deve conter 0 ou 1" in response.get_json()["error"]
