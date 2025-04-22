from flask import Flask, jsonify, send_from_directory, Response, request
import requests
from datetime import datetime
import os
from treino import treinar_e_exportar_modelo
from sklearn.tree import DecisionTreeClassifier
from sklearn.model_selection import train_test_split
import joblib
import pandas as pd
from utils.db import SessionLocal, Predicao

app = Flask(__name__)

# Caminho para o modelo
caminho_modelo = 'modelo/modelo_final.pkl'

# Verifica se o modelo existe
if not os.path.exists(caminho_modelo):
    print("Modelo não encontrado. Criando modelo...")
    treinar_e_exportar_modelo()

# Carrega o modelo
modelo = joblib.load(caminho_modelo)

# Rota para predição
@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Lista de campos obrigatórios
    campos_esperados = [
        'StudentID', 'Age', 'Gender', 'Ethnicity', 'ParentalEducation',
        'StudyTimeWeekly', 'Absences', 'Tutoring', 'ParentalSupport',
        'Extracurricular', 'Sports', 'Music', 'Volunteering', 'GPA'
    ]

    for campo in campos_esperados:
        if campo not in data:
            return jsonify({"error": f"Campo obrigatório ausente: {campo}"}), 400

    # Validações de valor
    idade = int(data['Age'])
    if idade < 5 or idade > 100:
        return jsonify({"error": "Idade fora dos limites permitidos (5 a 100)."}), 400

    gpa = float(data['GPA'])
    if gpa < 0 or gpa > 10:
        return jsonify({"error": "GPA fora dos limites permitidos (0.0 a 10.0)."}), 400

    booleanos = ['Tutoring', 'Extracurricular', 'Sports', 'Music', 'Volunteering']
    for campo in booleanos:
        if data[campo] not in [0, 1]:
            return jsonify({"error": f"O campo '{campo}' deve conter 0 ou 1."}), 400


    # Prepara entrada para o modelo
    colunas_usadas_no_modelo = [
        'StudyTimeWeekly', 'Absences', 'ParentalEducation', 'Ethnicity',
        'Gender', 'Tutoring', 'ParentalSupport', 'Extracurricular', 'Volunteering'
    ]
    df_model_input = pd.DataFrame([data])[colunas_usadas_no_modelo]

    prediction = int(modelo.predict(df_model_input)[0])
    proba = modelo.predict_proba(df_model_input)

    # Armazena no banco
    db = SessionLocal()
    nova_predicao = Predicao(
        student_id=data['StudentID'],
        age=idade,
        gender=data['Gender'],
        ethnicity=data['Ethnicity'],
        parental_education=data['ParentalEducation'],
        study_time_weekly=data['StudyTimeWeekly'],
        absences=data['Absences'],
        tutoring=data['Tutoring'],
        parental_support=data['ParentalSupport'],
        extracurricular=data['Extracurricular'],
        sports=data['Sports'],
        music=data['Music'],
        volunteering=data['Volunteering'],
        predicted_grade=str(prediction)
    )
    db.add(nova_predicao)
    db.commit()
    db.close()

    return jsonify({
        "GradeClass predito": prediction,
        "confiança": round(float(max(proba[0])) * 100, 2)
    })


# Rota para consultar todas as predições
@app.route('/predicoes', methods=['GET'])
def listar_predicoes():
    db = SessionLocal()
    resultados = db.query(Predicao).all()
    db.close()

    return jsonify([{
        'student_id': r.student_id,
        'predicted_grade': r.predicted_grade,
        'study_time_weekly': r.study_time_weekly,
        'absences': r.absences
    } for r in resultados])


# Rota para gerar relatório de estatísticas das predições
@app.route('/relatorio_predicoes', methods=['GET'])
def gerar_relatorio_predicoes():
    db = SessionLocal()
    resultados = db.query(Predicao).all()
    db.close()

    # Criar um DataFrame a partir dos resultados
    df = pd.DataFrame([{
        'student_id': r.student_id,
        'predicted_grade': r.predicted_grade,
        'study_time_weekly': r.study_time_weekly,
        'absences': r.absences
    } for r in resultados])

    # Calcular as estatísticas desejadas
    relatorio = {
        'total_predicoes': len(df),
        'media_predicoes': df['predicted_grade'].astype(float).mean(),
        'desvio_padrao_predicoes': df['predicted_grade'].astype(float).std(),
        'distribuicao_predicoes': df['predicted_grade'].value_counts().to_dict(),
    }

    # Converter o relatório em DataFrame e salvar em CSV
    relatorio_df = pd.DataFrame([relatorio])
    if not os.path.exists('relatorios'):
        os.makedirs('relatorios')

    relatorio_df.to_csv('relatorios/relatorio_predicoes.csv', index=False)

    # Retornar o caminho do arquivo gerado
    return jsonify({'message': 'Relatório gerado com sucesso!', 'file': 'relatorios/relatorio_predicoes.csv'})


# Rota para baixar o relatório
@app.route('/download_relatorio', methods=['GET'])
def download_relatorio():
    return send_from_directory(directory='relatorios', path='relatorio_predicoes.csv', as_attachment=True)


@app.route("/cria", methods=["GET"])
def cria_modelo():
    mensagem = treinar_e_exportar_modelo()

    return mensagem


@app.route('/', methods=['GET'])
def trending_cards_usage():
    return send_from_directory("templates", "index.html")


if __name__ == '__main__':
    app.run(port=int(os.environ.get("PORT", 5000)), debug=True)
