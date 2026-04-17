import sys
import os
import numpy as np
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar o core
sys.path.append(str(Path(__file__).parent.parent))
from core.meta_policy import MetaPolicy

def simulate_n9_cycle(seed, cycles=100):
    np.random.seed(seed)
    policy = MetaPolicy(entropy_threshold=0.15)
    
    results = []
    for i in range(cycles):
        # Simulação de cenário onde A1 é ligeiramente melhor
        # Mas queremos ver se o sistema mantém A2 e A3 vivos
        scores, entropy = policy.get_scores()
        action = policy.best_action()
        
        # Probabilidades de sucesso simuladas
        success_probs = {"A1": 0.85, "A2": 0.70, "A3": 0.60}
        reward = 1.0 if np.random.random() < success_probs[action] else 0.0
        
        policy.update(action, reward)
        results.append({"cycle": i, "action": action, "entropy": float(entropy)})
    
    return policy.get_distribution(), policy.calculate_entropy()

def run_multisseed_validation(num_seeds=10):
    print(f"🚀 Iniciando Validação Multisseed Nível 9 ({num_seeds} seeds)...")
    all_distributions = []
    all_entropies = []
    
    for s in range(num_seeds):
        dist, final_entropy = simulate_n9_cycle(s)
        all_distributions.append(dist)
        all_entropies.append(final_entropy)
        print(f"  Seed {s}: H = {final_entropy:.4f} | Dist: {dist}")

    avg_entropy = np.mean(all_entropies)
    std_entropy = np.std(all_entropies)
    
    avg_dist = {
        "A1": np.mean([d["A1"] for d in all_distributions]),
        "A2": np.mean([d["A2"] for d in all_distributions]),
        "A3": np.mean([d["A3"] for d in all_distributions])
    }

    report = {
        "avg_entropy": float(avg_entropy),
        "std_entropy": float(std_entropy),
        "avg_distribution": avg_dist,
        "diversity_maintained": bool(avg_dist["A2"] > 0.05 and avg_dist["A3"] > 0.05)
    }
    
    with open("logs/n9_validation_results.json", "w") as f:
        json.dump(report, f, indent=4)
    
    print("\n✅ Validação Concluída.")
    print(f"Média H: {avg_entropy:.4f} (±{std_entropy:.4f})")
    print(f"Distribuição Média: {avg_dist}")
    print(f"Diversidade Mantida: {report['diversity_maintained']}")

if __name__ == "__main__":
    run_multisseed_validation()
