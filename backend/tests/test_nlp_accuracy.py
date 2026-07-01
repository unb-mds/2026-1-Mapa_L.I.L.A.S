import os
import json
import pytest
from app.services.nlp_service import classificar_projeto

# Força o uso do mock caso não haja chave de API real configurada no ambiente.
# Dessa forma o CI não quebra se estiver testando PRs sem acesso aos secrets.
if not os.environ.get("GEMINI_API_KEY"):
    os.environ["USE_MOCK_IA"] = "true"

FIXTURE_PATH = os.path.join(os.path.dirname(__file__), "fixtures", "golden_dataset.json")

def test_nlp_accuracy_meets_threshold():
    """
    Carrega o Golden Dataset de PLs com suas classificações manuais esperadas.
    Calcula a taxa de acerto (Accuracy) do modelo NLP e exige um mínimo (ex: 90%).
    """
    if not os.path.exists(FIXTURE_PATH):
        pytest.skip("Golden dataset não encontrado. Pule.")

    with open(FIXTURE_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    if not dataset:
        pytest.skip("Golden dataset vazio.")

    acertos = 0
    total = len(dataset)

    for item in dataset:
        ementa = item.get("ementa", "")
        esperado = item.get("esperado", False)
        
        # Chama a inteligência do sistema
        resultado = classificar_projeto(ementa)
        
        if resultado == esperado:
            acertos += 1
        else:
            print("\n[ERRO DE CLASSIFICAÇÃO]")
            print(f"Ementa: {ementa}")
            print(f"Esperado: {esperado} | Recebido: {resultado}")

    accuracy = acertos / total
    
    print("\n[MÉTRICAS DO NLP]")
    print(f"Total: {total} | Acertos: {acertos} | Accuracy: {accuracy * 100:.2f}%")
    
    # Exige no mínimo 80% de acerto na semente inicial (ajustável pela SQUAD depois)
    assert accuracy >= 0.80, f"A acurácia do NLP caiu para {accuracy * 100:.2f}%. O mínimo esperado é 80%."
