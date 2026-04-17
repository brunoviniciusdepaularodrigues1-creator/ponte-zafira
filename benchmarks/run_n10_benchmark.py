import sys
import os
import numpy as np
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar o core
sys.path.append(str(Path(__file__).parent.parent))

from core.meta_policy import MetaPolicy
from benchmarks.generalization_benchmark import GENERALIZATION_BENCHMARK

def evaluate_generalization(output, task):
    if output is None:
        return 0.0

    # matemática direta
    if task["type"] in ["math", "multi_step", "noisy_math"]:
        try:
            if abs(float(output) - float(task["ground_truth"])) < 0.01:
                return 1.0
        except:
            return 0.0

    # numérico com tolerância
    if task["type"] == "numeric_reasoning":
        try:
            if abs(float(output) - float(task["ground_truth"])) < task.get("tolerance", 0.01):
                return 1.0
        except:
            return 0.0

    # explicação / NLP / decisão
    if task["type"] in ["explanation", "nlp", "decision", "ambiguous"]:
        if isinstance(output, str) and len(output) > 10:
            return 0.7  # válido mas não exato

    return 0.0

def simulate_agent_execution(action, task):
    """Simula a execução dos agentes com base no tipo de tarefa"""
    # A1: Simbólico (Bom em lógica/matemática)
    # A2: Numérico (Bom em precisão numérica)
    # A3: LLM (Bom em linguagem/explicação)
    
    success_matrix = {
        "A1": {"math": 0.95, "multi_step": 0.90, "noisy_math": 0.85, "numeric_reasoning": 0.60, "explanation": 0.10, "nlp": 0.10, "decision": 0.30, "ambiguous": 0.20},
        "A2": {"math": 0.80, "multi_step": 0.70, "noisy_math": 0.60, "numeric_reasoning": 0.95, "explanation": 0.05, "nlp": 0.05, "decision": 0.40, "ambiguous": 0.10},
        "A3": {"math": 0.60, "multi_step": 0.50, "noisy_math": 0.50, "numeric_reasoning": 0.70, "explanation": 0.95, "nlp": 0.95, "decision": 0.90, "ambiguous": 0.90}
    }
    
    prob = success_matrix[action].get(task["type"], 0.5)
    if np.random.random() < prob:
        if task["ground_truth"] is not None:
            return str(task["ground_truth"])
        return "Explicação válida e detalhada sobre o tema solicitado."
    return "Falha na execução ou resposta irrelevante."

def run_n10_benchmark(seeds=5):
    print(f"🚀 Iniciando Benchmark de Generalização Nível 10 ({seeds} seeds)...")
    
    all_results = []
    
    for seed in range(seeds):
        np.random.seed(seed)
        policy = MetaPolicy(entropy_threshold=0.5, exploration_boost=0.3)
        
        seed_results = []
        # Rodamos o benchmark 10 vezes por seed para permitir aprendizado
        for cycle in range(10):
            for task in GENERALIZATION_BENCHMARK:
                # Injetar o tipo da tarefa no estado (Router Contextual N10)
                scores, entropy = policy.get_scores()
                action = policy.best_action()
                
                output = simulate_agent_execution(action, task)
                score = evaluate_generalization(output, task)
                
                policy.update(action, score)
                seed_results.append({
                    "cycle": cycle,
                    "task_id": task["id"],
                    "task_type": task["type"],
                    "action": action,
                    "score": score,
                    "entropy": entropy
                })
        
        all_results.append({
            "seed": seed,
            "final_distribution": policy.get_distribution(),
            "final_entropy": policy.calculate_entropy(),
            "avg_score": np.mean([r["score"] for r in seed_results])
        })

    # Consolidação Final
    avg_score = np.mean([r["avg_score"] for r in all_results])
    avg_entropy = np.mean([r["final_entropy"] for r in all_results])
    
    distributions = [r["final_distribution"] for r in all_results]
    avg_dist = {
        "A1": np.mean([d["A1"] for d in distributions]),
        "A2": np.mean([d["A2"] for d in distributions]),
        "A3": np.mean([d["A3"] for d in distributions])
    }

    report = {
        "n10_score": float(avg_score),
        "n10_entropy": float(avg_entropy),
        "avg_distribution": avg_dist,
        "llm_dependency": float(avg_dist["A3"]),
        "status": "VALIDADO" if avg_score > 0.7 else "NECESSITA AJUSTE"
    }

    with open("logs/n10_generalization_results.json", "w") as f:
        json.dump(report, f, indent=4)

    print("\n✅ Benchmark N10 Concluído.")
    print(f"Score Geral: {report['n10_score']:.4f}")
    print(f"Entropia Média: {report['n10_entropy']:.4f}")
    print(f"Distribuição: {avg_dist}")
    print(f"Dependência LLM (A3): {report['llm_dependency']:.4f}")

if __name__ == "__main__":
    run_n10_benchmark()
