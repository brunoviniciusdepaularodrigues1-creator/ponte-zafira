import json
import argparse
import numpy as np
import os

def calculate_metrics(log_path):
    if not os.path.exists(log_path):
        print(f"Erro: Log {log_path} não encontrado.")
        return

    divergences = []
    consistencies = []
    learning_deltas = []
    
    with open(log_path, 'r') as f:
        for line in f:
            try:
                entry = json.loads(line)
                
                # 1. Divergence Score (baseado nas probabilidades de seleção)
                probs = entry.get("selection_probs", [])
                if probs:
                    # Entropia como medida de divergência/incerteza
                    entropy = -sum(p * np.log(p + 1e-9) for p in probs)
                    divergences.append(entropy)
                
                # 2. Judge Consistency
                # Verifica se o agente selecionado foi realmente o melhor ou próximo disso
                final_scores = entry.get("final_scores", {})
                selected = entry.get("selected_agent")
                if final_scores and selected:
                    best_score = max(final_scores.values())
                    selected_score = final_scores.get(selected, 0)
                    consistencies.append(1.0 if selected_score >= best_score - 0.1 else 0.0)
                
                # 3. Controller Learning
                pre = entry.get("pre_policy", {})
                post = entry.get("post_policy", {})
                if pre and post:
                    delta = 0
                    for agent_type in pre:
                        delta += abs(post[agent_type]["score"] - pre[agent_type]["score"])
                    learning_deltas.append(delta)
                    
            except Exception as e:
                continue

    if not divergences:
        print("Nenhum dado válido encontrado no log.")
        return

    avg_divergence = np.mean(divergences)
    avg_consistency = np.mean(consistencies)
    total_delta = sum(learning_deltas)
    learning_ratio = total_delta / len(learning_deltas) if learning_deltas else 0

    print(f"--- MÉTRICAS DE VALIDAÇÃO MULTIAGENTE ---")
    print(f"divergence_score: {avg_divergence:.4f}")
    print(f"judge_consistency: {avg_consistency:.4f}")
    print(f"controller_learning_delta: {total_delta:.4f}")
    print(f"controller_learning_ratio: {learning_ratio:.4f}")
    print(f"---------------------------------------")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", type=str, default="agent_evolution_v75_log.txt")
    args = parser.parse_args()
    calculate_metrics(args.log)
