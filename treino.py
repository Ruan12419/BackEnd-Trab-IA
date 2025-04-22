# bibliotecas para operações com dados
import pandas as pd
import numpy as np

# bibliotecas de visualização
import matplotlib.pyplot as plt
import seaborn as sns

# avaliação de modelos
from sklearn.metrics import accuracy_score, confusion_matrix, classification_report
from sklearn.model_selection import train_test_split

# modelos de machine learning
from sklearn.tree import DecisionTreeClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import joblib

# SMOTE
from imblearn.over_sampling import SMOTE

def treinar_e_exportar_modelo():
    
    performance_estudantes = pd.read_csv("Student_performance_data.csv", encoding='latin1')
    performance_estudantes = performance_estudantes.round(2)

    X = performance_estudantes[['StudyTimeWeekly','Absences','ParentalEducation','Ethnicity','Gender', 'Tutoring', 'ParentalSupport', 'Extracurricular', 'Volunteering']]
    Y = performance_estudantes['GradeClass']

    n_iter = 100
    np.random.seed(19)

    acc_log = []
    acc_tree = []
    acc_rf = []

    for i in range(n_iter + 1):
        # Split dos dados
        X_train, X_test, y_train, y_test = train_test_split(X, Y, stratify=Y, test_size=0.2)

        # Aplica SMOTE no conjunto de treino
        smote = SMOTE(random_state=19)
        X_train_sm, y_train_sm = smote.fit_resample(X_train, y_train)

        # Regressão Logística
        log_model = LogisticRegression(max_iter=1000)
        log_model.fit(X_train_sm, y_train_sm)
        pred_log = log_model.predict(X_test)
        acc_log.append(accuracy_score(y_test, pred_log))

        # Árvore de Decisão
        tree_model = DecisionTreeClassifier(max_depth=3)
        tree_model.fit(X_train_sm, y_train_sm)
        pred_tree = tree_model.predict(X_test)
        acc_tree.append(accuracy_score(y_test, pred_tree))

        # Random Forest
        rf_model = RandomForestClassifier(n_estimators=100, random_state=19)
        rf_model.fit(X_train_sm, y_train_sm)
        pred_rf = rf_model.predict(X_test)
        acc_rf.append(accuracy_score(y_test, pred_rf))

    # Resultados
    print(f"Acurácia - Regressão Logística: {np.mean(acc_log):.2f}")
    print(f"Acurácia - Árvore de Decisão: {np.mean(acc_tree):.2f}")
    print(f"Acurácia - Random Forest: {np.mean(acc_rf):.2f}")

    # Matriz de confusão e relatório de classificação
    print("\nMatriz de Confusão e Relatório de Classificação - Random Forest:")
    matriz_confusao = confusion_matrix(y_test, pred_rf)
    relatorio_classificacao = classification_report(y_test, pred_rf, zero_division=0)
    print(matriz_confusao)
    print(relatorio_classificacao)

    # Média das acurácias
    mean_acc = {
        'Logistic Regression': np.mean(acc_log),
        'Decision Tree': np.mean(acc_tree),
        'Random Forest': np.mean(acc_rf)
    }

    print("\nMédias de Acurácia dos Modelos:")
    for modelo, acc in mean_acc.items():
        print(f"{modelo}: {acc:.4f}")

    melhor_modelo_nome = max(mean_acc, key=mean_acc.get)
    print(f"\nMelhor modelo: {melhor_modelo_nome}")

    # Treina o melhor modelo com todo o conjunto balanceado
    smote_full = SMOTE(random_state=19)
    X_bal, Y_bal = smote_full.fit_resample(X, Y)

    if melhor_modelo_nome == 'Logistic Regression':
        modelo_final = LogisticRegression(max_iter=1000)
    elif melhor_modelo_nome == 'Decision Tree':
        modelo_final = DecisionTreeClassifier(max_depth=3)
    else:
        modelo_final = RandomForestClassifier(n_estimators=100, random_state=19)

    modelo_final.fit(X_bal, Y_bal)

    # Exporta modelo
    nome_arquivo = f"modelo/modelo_final.pkl"
    joblib.dump(modelo_final, nome_arquivo)

    return f"\nModelo exportado em: {nome_arquivo}"
