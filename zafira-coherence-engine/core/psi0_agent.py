import time
import os
import sys
import json
import random
import math
from datetime import datetime

# Adiciona a raiz do projeto ao sys.path para permitir imports de core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_executor import process, save_results
from core.psi0_ranker import rank_results
from core.executor_mutator import create_variant
from core.psi0_state_encoder import encode_state

# Arquivos de feedback dos múltiplos executores (Rede Heterogênea)
FEEDBACK_FILES = [
    "executor_agent/execution_result.json",
    "executor_agent_v2/execution_result_v2.json",
    "executor_llm/execution_result_llm.json"
]

class Psi0Agent:
    def __init__(self, interval=5):
        self.interval = interval
        self.generation = 0
        self.learning_rate = 0.1
        
        # Caminhos absolutos
        self.policy_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_policy.json"))
        self.memory_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_memory.jsonl"))
        
        self.policy = self._load_policy()

    def _load_policy(self):
        if os.path.exists(self.policy_file):
            with open(self.policy_file, "r") as f:
                return json.load(f)
        return {
            "C": {"v1": 0.3, "v2": 0.5, "llm": 0.9},
            "F": {"v1": 0.8, "v2": 0.6, "llm": 0.7},
            "A": {"v1": 0.9, "v2": 0.4, "llm": 0.5}
        }

    def _save_policy(self):
        with open(self.policy_file, "w") as f:
            json.dump(self.policy, f, indent=2)

    def log_experience(self, experience):
        """Salva a experiência estruturada no log de memória."""
        with open(self.memory_file, "a") as f:
            f.write(json.dumps(experience, ensure_ascii=False) + "\n")

    def internal_evaluate(self, executor, result_data, top_decision):
        """Avaliação Interna de Score."""
        base_score = result_data.get("score", 0.5)
        stage = top_decision.get("stage", "F")
        coherence = top_decision.get("coherence", 0.5)
        
        penalty = 0
        if stage == "C" and executor == "v1": penalty = 0.2
        if stage == "A" and executor == "llm": penalty = 0.1
        
        internal_score = (base_score * 0.6) + (coherence * 0.4) - penalty
        return round(max(0, min(1, internal_score)), 2)

    def select_strategy_probabilistic(self, top_decision, temperature=0.2):
        """Seleção Probabilística (Softmax + Sampling)."""
        stage = top_decision.get("stage", "F")
        if stage not in self.policy: stage = "F"
            
        executors = list(self.policy[stage].keys())
        scores = [self.policy[stage][exe] for exe in executors]
        
        exp_scores = [math.exp(s / temperature) for s in scores]
        sum_exp = sum(exp_scores)
        probs = [e / sum_exp for e in exp_scores]
        
        chosen = random.choices(executors, weights=probs, k=1)[0]
        return chosen, probs

    def update_policy(self, stage, executor, reward):
        """Policy Learning Loop."""
        if stage not in self.policy: stage = "F"
        old_value = self.policy[stage][executor]
        new_value = old_value + self.learning_rate * (reward - old_value)
        self.policy[stage][executor] = round(new_value, 4)
        self._save_policy()
        return old_value, new_value

    def read_all_feedbacks(self):
        feedbacks = []
        for f_path in FEEDBACK_FILES:
            try:
                if os.path.exists(f_path):
                    with open(f_path, "r") as f:
                        data = json.load(f)
                        executor_id = data.get("executor", "v1" if "v1" in f_path else ("v2" if "v2" in f_path else "llm"))
                        score = data.get("score", 0.5)
                        config = data.get("config", {})
                        feedbacks.append({"executor": executor_id, "score": score, "config": config})
            except Exception: pass
        return feedbacks

    def run(self):
        print("Zafira Coherence Engine: Psi0Agent Evolutivo Iniciado...")
        try:
            while True:
                print("\n--- Ciclo de Aprendizado Cognitivo ---")
                results = process()
                if not results:
                    time.sleep(self.interval)
                    continue
                
                ranked = rank_results(results)
                save_results(ranked)
                top = ranked[0]

                # 🔥 CAMADA 1: State Encoding
                history_stats = {"llm_success": 0.9, "v1_success": 0.8, "v2_success": 0.7}
                state_vector = encode_state(top.get("stage"), top.get("input"), history_stats)
                print(f"Estado Vetorial (Camada 1): {state_vector}")

                # Seleção Probabilística
                chosen_executor, probs = self.select_strategy_probabilistic(top)
                
                # Simulação de leitura de resultado
                internal_score = 0.5
                res_path = f"executor_{'agent' if chosen_executor=='v1' else ('agent_v2' if chosen_executor=='v2' else 'llm')}/execution_result{'_v2' if chosen_executor=='v2' else ('_llm' if chosen_executor=='llm' else '')}.json"
                if os.path.exists(res_path):
                    with open(res_path, "r") as f:
                        res_data = json.load(f)
                        internal_score = self.internal_evaluate(chosen_executor, res_data, top)
                
                # 1. Registrar Experiência
                experience = {
                    "timestamp": datetime.now().isoformat(),
                    "input_stage": top["stage"],
                    "executor": chosen_executor,
                    "internal_score": internal_score,
                    "coherence": top.get("coherence", 0.5)
                }
                self.log_experience(experience)

                # 2. Policy Learning Loop
                old_val, new_val = self.update_policy(top["stage"], chosen_executor, internal_score)

                # 3. Exportar Estado Completo (Persistência da Camada 1)
                feedbacks = self.read_all_feedbacks()
                bridge_data = {
                    "agent": "zafira-psi0",
                    "timestamp": datetime.now().isoformat(),
                    "state_vector": state_vector, # 🔥 AQUI ESTÁ O CAMPO
                    "chosen_executor": chosen_executor,
                    "internal_score": internal_score,
                    "probabilities": probs,
                    "policy_update": {"old": old_val, "new": new_val},
                    "best_decision": top,
                    "ranking": ranked,
                    "network_status": feedbacks
                }

                # Escrita atômica para evitar arquivos corrompidos
                with open("bridge_interface.json.tmp", "w") as f:
                    json.dump(bridge_data, f, indent=2, ensure_ascii=False)
                os.replace("bridge_interface.json.tmp", "bridge_interface.json")
                
                print(f"Estado persistido no bridge com state_vector: {state_vector}")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nPsi0Agent finalizado.")

if __name__ == "__main__":
    agent = Psi0Agent()
    agent.run()
