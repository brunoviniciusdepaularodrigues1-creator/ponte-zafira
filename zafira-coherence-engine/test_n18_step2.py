import sys
import os
import json
import numpy as np
from datetime import datetime

# Adiciona a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_agent import Psi0Agent
from core.psi0_executor import save_results
from core.psi0_ranker import rank_results

class N18TestAgent(Psi0Agent):
    def run_test(self, tasks):
        print("Zafira Coherence Engine: Iniciando Teste Misto N18 Passo 2...")
        results_log = []
        
        for i, task_input in enumerate(tasks):
            print(f"\n--- Tarefa {i+1}: {task_input} ---")
            
            # Simula o processamento da tarefa
            task_data = {
                "input": task_input,
                "stage": "F", # Default stage
                "coherence": 0.5,
                "structure": 0.5,
                "variation": 0.5
            }
            ranked = rank_results([task_data])
            top = ranked[0]
            
            # Encoding e Latent
            history_stats = {"llm_success": 0.9, "v1_success": 0.8, "v2_success": 0.7}
            from core.psi0_state_encoder import encode_state
            state_vector = encode_state(top.get("stage"), top.get("input"), history_stats)
            latent = self.encoder.encode(np.array(state_vector))
            
            # Routing
            from core.psi0_router import classify_task, get_strategy_bias
            task_type = classify_task(task_input)
            strategy_bias = get_strategy_bias(task_type)
            
            raw_probs = self.actor.softmax(top["stage"])
            blended_probs = self.coherence.apply_contextual_bias(raw_probs, strategy_bias)
            
            meta_scores = self.meta.get_scores(task_type)
            total_meta_score = sum(meta_scores.values())
            meta_probs = {k: v / total_meta_score if total_meta_score > 0 else 1/len(meta_scores) for k, v in meta_scores.items()}
            
            final_probs = {}
            for action in blended_probs:
                final_probs[action] = (0.7 * blended_probs[action]) + (0.3 * meta_probs.get(action, 0))
            
            total_final_probs = sum(final_probs.values())
            final_probs = {k: v / total_final_probs for k, v in final_probs.items()}
            
            # 🔥 N18 Passo 2: Memory Bias
            preferred = self.meta.get_preference(task_type)
            print(f"  Preferência da Memória (MetaOrchestrator): {preferred}")
            
            if preferred is not None and preferred in final_probs:
                memory_bias = 0.05
                final_probs[preferred] += memory_bias
                total_final_probs = sum(final_probs.values())
                final_probs = {k: v / total_final_probs for k, v in final_probs.items()}
            
            print(f"  Selection Probs: {final_probs}")
            
            # Seleção
            import random
            chosen_action = random.choices(list(final_probs.keys()), weights=list(final_probs.values()))[0]
            from core.action_space import ACTIONS
            chosen_executor = ACTIONS[chosen_action]
            print(f"  Selected Agent Type: {chosen_action} ({chosen_executor})")
            
            # Execução
            from core.dispatcher import execute
            output = execute(chosen_action, task_input)
            print(f"  Execução: {output}")
            
            # Reward e Update
            # (Simulando um internal_score para o teste)
            internal_score = 0.8 if output is not None else 0.2
            self.meta.update(task_type, chosen_action, internal_score)
            
            # Judge Consistency (Simulado para o log)
            judge_consistency = 0.9 if internal_score > 0.5 else 0.3
            print(f"  Judge Consistency: {judge_consistency}")
            
            results_log.append({
                "task": task_input,
                "type": task_type,
                "preferred": preferred,
                "probs": final_probs,
                "selected": chosen_action,
                "consistency": judge_consistency
            })
            
        return results_log

if __name__ == "__main__":
    tasks = [
        "solve x**2 - 4 = 0",
        "solve 2*x + 5 = 15",
        "calculate 7 * 7 + 1",
        "calculate 100 / 4 - 5",
        "Explain artificial intelligence in one sentence.",
        "What is the capital of France?"
    ]
    
    agent = N18TestAgent()
    results = agent.run_test(tasks)
    
    # Salva o bridge final para inspeção
    bridge_data = {
        "meta_policy_stats": agent.meta.stats,
        "test_results": results
    }
    with open("bridge_interface.json", "w") as f:
        json.dump(bridge_data, f, indent=2)
    
    print("\n--- Resumo do Teste ---")
    print(f"Learning Delta (Total Updates): {len(tasks)}")
