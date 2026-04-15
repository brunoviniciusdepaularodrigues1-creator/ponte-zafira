import os
import sys
import json

# Adiciona a raiz do projeto ao sys.path para permitir imports de core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_controller import Psi0Controller
from core.psi0_parser import extract_features
from core.psi0_formatter import format_output
from core.psi0_ranker import rank_results

INPUT_DIR = "input_bruto"
OUTPUT_DIR = "feedback_real"

controller = Psi0Controller()

def read_inputs():
    if not os.path.exists(INPUT_DIR):
        os.makedirs(INPUT_DIR)
        return []
    
    files = os.listdir(INPUT_DIR)
    data = []

    for f in files:
        file_path = os.path.join(INPUT_DIR, f)
        if os.path.isfile(file_path):
            with open(file_path, "r") as file:
                content = file.read()
                data.append(content)

    return data

def process(adjustment=0.5):
    inputs = read_inputs()
    results = []

    for item in inputs:
        # Extração de características estruturais (Camada F)
        features = extract_features(item)

        # Cálculo normalizado de energia (E) para estabilidade
        E = (
            (features["length"] / 100) * 0.3 +
            (features["word_count"] / 50) * 0.3 +
            features["complexity"] * 0.4
        )

        # Aplicação do ajuste de feedback (Learning - L)
        # O ajuste influencia a percepção de energia do sistema
        E = E * (1 + adjustment * 0.1)

        history = controller.run_cycle(E, steps=10)
        final = history[-1]

        # Formatação estruturada (Camada Semântica)
        formatted = format_output(item, final)
        results.append(formatted)

    return results

def save_results(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "result.json"), "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Execução padrão sem ajuste externo
    results = process()
    ranked = rank_results(results)
    save_results(ranked)
