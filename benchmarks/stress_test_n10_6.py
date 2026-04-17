import sys
import os
import numpy as np
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar o core
sys.path.append(str(Path(__file__).parent.parent))

from core.meta_policy import MetaPolicy
from core.psi0_router import classify_task, get_strategy_bias

STRESS_BENCHMARK = [
    # 🍌 Entrada Absurda
    {
        "id": "stress_1",
        "input": "calcule a raiz da consciência dividida por banana",
        "type": "absurd",
        "ground_truth": None
    },
    # ⚖️ Conflito de Agentes (Lógica vs Fato Errado)
    {
        "id": "stress_2",
        "input": "se 2+2=5, quanto é 5+5?",
        "type": "conflict",
        "ground_truth": 12.5 # Se 1=1.25, então 10=12.5 (lógica hipotética)
    },
    # 🧪 Ruído Extremo
    {
        "id": "stress_3",
        "input": "   99///3   ??? ",
        "type": "noisy_math",
        "ground_truth": 33
    },
    # 🧩 Ambiguidade Pesada
    {
        "id": "stress_4",
        "input": "o que é melhor: ser ou não ser?",
        "type": "deep_ambiguity",
        "ground_truth": None
    },
    # 🌀 Paradoxos
    {
        "id": "stress_5",
        "input": "esta frase é falsa",
        "type": "paradox",
        "ground_truth": None
    }
]

def compute_entropy(probs):
    p_values = np.array(list(probs.values()))
    p_values = p_values[p_values > 0]
    if len(p_values) <= 1: return 0.0
    return -np.sum(p_values * np.log2(p_values))

def evaluate_stress_response(action, output, task):
    """Avalia a resiliência da resposta sob estresse."""
    if output is None or "error" in str(output).lower():
        return 0.1 # Falha crítica
    
    # Absurdo/Ambiguidade: Espera-se que A3 (LLM) lide com a semântica sem travar
    if task["type"] in ["absurd", "deep_ambiguity", "paradox"]:
        if action == "A3" and len(str(output)) > 15:
            return 0.8 # Sucesso qualitativo
        return 0.3 # Agente errado para a tarefa
    
    # Ruído/Conflito: Espera-se que A1 ou A2 resolvam a lógica
    if task["type"] in ["noisy_math", "conflict"]:
        try:
            val = float(output)
            if abs(val - float(task["ground_truth"])) < 0.1:
                return 1.0
            return 0.4 # Resposta numérica errada mas formato correto
        except:
            return 0.2
            
    return 0.5

def simulate_stress_execution(action, task):
    """Simula comportamento sob estresse."""
    # Simulação de A1/A2 falhando em absurdos e A3 sendo o único a dar saída coerente
    if task["type"] in ["absurd", "deep_ambiguity", "paradox"]:
        if action == "A3": return "Resposta filosófica ou semântica sobre o input."
        return "Erro: Operação inválida para o domínio."
    
    if task["type"] == "noisy_math":
        if action in ["A1", "A2"]: return str(task["ground_truth"])
        return "O input parece conter ruído matemático."
        
    if task["type"] == "conflict":
        if action == "A1": return str(task["ground_truth"])
        return "2+2 é 4, mas se você diz que é 5..."
        
    return "Processamento padrão."

def run_n10_6_stress_test(cycles=100):
    print(f"🚀 Iniciando Stress Test Nível 10.6 ({cycles} ciclos)...")
    policy = MetaPolicy(entropy_threshold=0.5, exploration_boost=0.3)
    
    history = []
    
    for i in range(cycles):
        task = np.random.choice(STRESS_BENCHMARK)
        
        # Simulação do Adaptive Entropy Router (N10.5)
        # 1. Pegar scores da MetaPolicy
        meta_scores, current_h = policy.get_scores()
        
        # 2. Modulação Adaptativa de Pesos
        if current_h > 0.7:
            mw, cw = 0.5, 0.5
        elif current_h < 0.4:
            mw, cw = 0.2, 0.8
        else:
            mw, cw = 0.3, 0.7
            
        # 3. Simular Blended Probs (Simplificado para o teste)
        # Bias de estratégia baseado no tipo
        bias = {"A1": 0.33, "A2": 0.33, "A3": 0.34}
        if task["type"] in ["absurd", "deep_ambiguity"]: bias = {"A1": 0.1, "A2": 0.1, "A3": 0.8}
        
        final_probs = {k: (cw * bias[k] + mw * (meta_scores[k]/sum(meta_scores.values()))) for k in bias}
        
        action = np.random.choice(list(final_probs.keys()), p=[final_probs[k]/sum(final_probs.values()) for k in final_probs])
        
        output = simulate_stress_execution(action, task)
        score = evaluate_stress_response(action, output, task)
        
        policy.update(action, score)
        
        history.append({
            "cycle": i,
            "task_type": task["type"],
            "action": action,
            "entropy": current_h,
            "score": score
        })

    # Análise de Saturação e Colapso
    final_h = policy.calculate_entropy()
    avg_score = np.mean([h["score"] for h in history])
    dist = policy.get_distribution()
    
    # Detecção de Colapso: Se um agente tem > 90% ou < 2%
    collapse = any(v > 0.9 or v < 0.02 for v in dist.values())
    
    report = {
        "cycles": cycles,
        "final_entropy": float(final_h),
        "avg_score": float(avg_score),
        "distribution": dist,
        "collapse_detected": bool(collapse),
        "resilience_status": "ALTA" if not collapse and avg_score > 0.6 else "VULNERÁVEL"
    }
    
    with open("logs/n10_6_stress_results.json", "w") as f:
        json.dump(report, f, indent=4)
        
    print("\n✅ Stress Test N10.6 Concluído.")
    print(f"Entropia Final: {final_h:.4f}")
    print(f"Score Médio: {avg_score:.4f}")
    print(f"Distribuição: {dist}")
    print(f"Colapso Detectado: {collapse}")
    print(f"Status de Resiliência: {report['resilience_status']}")

if __name__ == "__main__":
    run_n10_6_stress_test()
