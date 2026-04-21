import os
import sys
import json
import random

# Adiciona a raiz do projeto ao sys.path para permitir imports de core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_controller import Psi0Controller
from core.psi0_parser import extract_features
from core.psi0_formatter import format_output
from core.psi0_ranker import rank_results

INPUT_DIR = "input_bruto"
OUTPUT_DIR = "feedback_real"

controller = Psi0Controller()

BENCHMARK_TASKS = [
    "solve x**2 - 4 = 0", # Symbolic
    "calculate 15 * 3 + 2", # Numeric
    "What is the capital of France?", # LLM
    "simplify (a + b)**2", # Symbolic
    "find the square root of 81", # Numeric
    "Explain artificial intelligence in one sentence.", # LLM
    "solve 2*y + 5 = 15", # Symbolic
    "calculate 100 / 4 - 5", # Numeric
    "Who wrote 'Don Quixote'?", # LLM
    "solve x**3 - 8 = 0", # Symbolic
    "calculate 7 * 7 + 1", # Numeric
    "What is the highest mountain in the world?" # LLM
]

def process(adjustment=0.5):
    # Seleciona uma tarefa aleatória da lista de benchmark
    item = random.choice(BENCHMARK_TASKS)

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
    
    # Retorna uma lista contendo apenas o resultado da tarefa selecionada
    return [formatted]

def save_results(results):
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    with open(os.path.join(OUTPUT_DIR, "result.json"), "w") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    # Execução padrão sem ajuste externo
    results = process()
    ranked = rank_results(results)
    save_results(ranked)
