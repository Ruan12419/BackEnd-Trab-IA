function mostrarTela(tela) {
    document.querySelectorAll('.container').forEach(c => c.classList.remove('active'));
    document.getElementById(tela).classList.add('active');

    if (tela === 'formulario') {
        document.getElementById('btnFormulario').classList.remove('disabled');
        document.getElementById('btnDashboard').classList.add('disabled');
    } else if (tela === 'dashboard') {
        document.getElementById('btnFormulario').classList.add('disabled');
        document.getElementById('btnDashboard').classList.remove('disabled');
    }

    if (tela === 'dashboard') {
        carregarDashboard();
    }
}

function enviarDados() {
    const idade = parseInt(document.getElementById('age').value);
    const studyTime = parseFloat(document.getElementById('studyTimeWeekly').value);
    const absences = parseInt(document.getElementById('absences').value);
    const gpa = parseFloat(document.getElementById('gpa').value);

    const camposObrigatorios = [
        { id: 'studentID', nome: 'ID do Aluno' },
        { id: 'age', nome: 'Idade' },
        { id: 'ethnicity', nome: 'Etnia' },
        { id: 'parentalEducation', nome: 'Educação dos Pais' },
        { id: 'studyTimeWeekly', nome: 'Horas de Estudo por Semana' },
        { id: 'absences', nome: 'Número de Faltas' },
        { id: 'parentalSupport', nome: 'Apoio dos Pais' },
        { id: 'gpa', nome: 'GPA' }
    ];

    for (const campo of camposObrigatorios) {
        const valor = document.getElementById(campo.id).value;
        if (!valor || valor.trim() === "") {
            alert(`Preencha o campo obrigatório: ${campo.nome}`);
            return;
        }
    }

    // Radios obrigatórios (com valor 0 ou 1)
    const radiosObrigatorios = [
        { nome: 'gender', label: 'Gênero' },
        { nome: 'tutoring', label: 'Reforço Escolar' },
        { nome: 'extracurricular', label: 'Atividades Extracurriculares' },
        { nome: 'sports', label: 'Esportes' },
        { nome: 'music', label: 'Música' },
        { nome: 'volunteering', label: 'Voluntariado' }
    ];

    for (const radio of radiosObrigatorios) {
        if (!document.querySelector(`input[name="${radio.nome}"]:checked`)) {
            alert(`Selecione uma opção para: ${radio.label}`);
            return;
        }
    }

    if (idade < 5 || idade > 100) {
        alert("Idade deve estar entre 5 e 100 anos.");
        return;
    }
    if (isNaN(gpa) || gpa < 0 || gpa > 10) {
        alert("GPA deve estar entre 0.0 e 10.0.");
        return;
    }

    const dadosAluno = {
        "StudentID": document.getElementById('studentID').value.trim(),
        "Age": idade,
        "Gender": parseInt(document.querySelector('input[name="gender"]:checked').value),
        "Ethnicity": document.getElementById('ethnicity').value,
        "ParentalEducation": document.getElementById('parentalEducation').value,
        "StudyTimeWeekly": studyTime,
        "Absences": absences,
        "Tutoring": parseInt(document.querySelector('input[name="tutoring"]:checked').value),
        "ParentalSupport": parseInt(document.getElementById('parentalSupport').value),
        "Extracurricular": parseInt(document.querySelector('input[name="extracurricular"]:checked').value),
        "Sports": parseInt(document.querySelector('input[name="sports"]:checked').value),
        "Music": parseInt(document.querySelector('input[name="music"]:checked').value),
        "Volunteering": parseInt(document.querySelector('input[name="volunteering"]:checked').value),
        "GPA": gpa
    };

    fetch('http://192.168.0.17:5000/predict', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(dadosAluno)
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Erro: " + data.error);
        } else {
            document.querySelector("#p-resultado").innerHTML =
                "Predição: GRAU " + data["GradeClass predito"] +
                " (" + data["confiança"] + "% de confiança)";
        }
    })
    .catch(error => {
        alert("Erro ao enviar os dados");
        console.error(error);
    });
}

async function gerarRelatorio() {
    try {
    
        const response = await fetch('/relatorio_predicoes', {
            method: 'GET',
        });

    
        if (!response.ok) {
            throw new Error('Falha ao gerar o relatório');
        }

        const data = await response.json();
    
        console.log(data.message);
        
        const btnBaixarRelatorio = document.getElementById("btnBaixarRelatorio");
        btnBaixarRelatorio.classList.remove("disabled");
        btnBaixarRelatorio.classList.add("enabled");
    
        window.relatorioFilePath = data.file;

    } catch (error) {
        console.error('Erro ao gerar o relatório:', error);
    }
}

function baixarRelatorio() {
    const botao = document.getElementById("btnBaixarRelatorio");

    if (botao.classList.contains("disabled")) {
        alert("Botão desabilitado. Gere o relatório primeiro.");
        return; 
    }

    fetch("http://192.168.0.17:5000/download_relatorio")
        .then((response) => {
            if (!response.ok) {
                throw new Error('Falha ao baixar o relatório');
            }
            return response.blob();
        })
        .then((blob) => {
            const url = URL.createObjectURL(blob);
            const link = document.createElement('a');
            link.href = url;
            link.download = 'relatorio_predicoes.csv';
            link.click();
            URL.revokeObjectURL(url);
        })
        .catch((error) => {
            console.error('Erro ao baixar o relatório:', error);
        });
}



function carregarDashboard() {

            fetch('http://192.168.0.17:5000/predicoes')
                .then(res => res.json())
                .then(predicoes => {
                
                    const classes = {};
                    predicoes.forEach(p => {
                        const c = p.predicted_grade;
                        classes[c] = (classes[c] || 0) + 1;
                    });

                    const ctxDistribuicao = document.getElementById('graficoDistribuicao').getContext('2d');
                    new Chart(ctxDistribuicao, {
                        type: 'bar',
                        data: {
                            labels: Object.keys(classes),
                            datasets: [{
                                label: 'Distribuição por Classe',
                                data: Object.values(classes),
                                backgroundColor: '#4CAF50'
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                y: { beginAtZero: true }
                            }
                        }
                    });

                
                    const total = predicoes.length;
                    const mediaAbsences = predicoes.reduce((sum, p) => sum + parseFloat(p.absences), 0) / total;
                    const mediaStudyTime = predicoes.reduce((sum, p) => sum + parseFloat(p.study_time_weekly), 0) / total;
                    const mediaPredictedGrade = predicoes.reduce((sum, p) => sum + parseFloat(p.predicted_grade), 0) / total;

                    const stdAbsences = Math.sqrt(predicoes.reduce((acc, p) => acc + Math.pow(parseFloat(p.absences) - mediaAbsences, 2), 0) / total);
                    const stdStudyTime = Math.sqrt(predicoes.reduce((acc, p) => acc + Math.pow(parseFloat(p.study_time_weekly) - mediaStudyTime, 2), 0) / total);
                    const stdPredictedGrade = Math.sqrt(predicoes.reduce((acc, p) => acc + Math.pow(parseFloat(p.predicted_grade) - mediaPredictedGrade, 2), 0) / total);

                    document.getElementById('estatisticas').innerHTML = `
        <p>Total de predições: ${total}</p>
        <p>Média de faltas: ${mediaAbsences.toFixed(2)}</p>
        <p>Desvio padrão de faltas: ${stdAbsences.toFixed(2)}</p>
        <p>Média de horas de estudo: ${mediaStudyTime.toFixed(2)}</p>
        <p>Desvio padrão de horas de estudo: ${stdStudyTime.toFixed(2)}</p>
        <p>Média das notas previstas: ${mediaPredictedGrade.toFixed(2)}</p>
        <p>Desvio padrão das notas previstas: ${stdPredictedGrade.toFixed(2)}</p>
    `;

                
                    const ctxEstudoVsFaltas = document.getElementById('graficoEstudoVsFaltas').getContext('2d');
                    new Chart(ctxEstudoVsFaltas, {
                        type: 'scatter',
                        data: {
                            datasets: [{
                                label: 'Tempo de Estudo vs Faltas',
                                data: predicoes.map(p => ({
                                    x: p.study_time_weekly,
                                    y: p.absences
                                })),
                                backgroundColor: '#FF5733',
                                borderColor: '#FF5733',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    type: 'linear',
                                    position: 'bottom',
                                    title: {
                                        display: true,
                                        text: 'Horas de Estudo por Semana'
                                    }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Faltas'
                                    }
                                }
                            }
                        }
                    });

                
                    const ctxPredicaoNotas = document.getElementById('graficoPredicaoNotas').getContext('2d');
                    new Chart(ctxPredicaoNotas, {
                        type: 'scatter',
                        data: {
                            datasets: [{
                                label: 'Predição de Notas por Estudante',
                                data: predicoes.map(p => ({
                                    x: p.student_id,
                                    y: p.predicted_grade
                                })),
                                backgroundColor: '#3B9AC4',
                                borderColor: '#3B9AC4',
                                borderWidth: 1
                            }]
                        },
                        options: {
                            responsive: true,
                            scales: {
                                x: {
                                    title: {
                                        display: true,
                                        text: 'ID do Estudante'
                                    }
                                },
                                y: {
                                    title: {
                                        display: true,
                                        text: 'Nota Predita'
                                    }
                                }
                            }
                        }
                    });
                });
}

