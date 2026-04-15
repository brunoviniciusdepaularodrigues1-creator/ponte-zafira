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
from core.psi0_reward import compute_reward
from core.psi0_value_function import ValueFunction
from core.psi0_actor import PolicyActor

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
        
        self.value_fn = ValueFunction()
        self.actor = PolicyActor()

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

                # 🔥 CAMADA 5 (Corrigida): Arbitragem de Decisão
                stage = top["stage"]
                
                # 1. Actor sugere
                actor_choice, actor_probs = self.actor.select(stage)

                # 2. Value sugere (predictions de cada executor)
                executors = ["v1", "v2", "llm"]
                predictions = []
                for exe in executors:
                    value = self.value_fn.predict(state_vector, stage, exe)
                    predictions.append((exe, value))

                value_choice = max(predictions, key=lambda x: x[1])[0]

                # 3. Arbitrador Final - Consenso ou Fallback
                if actor_choice == value_choice:
                    chosen_executor = actor_choice
                else:
                    # Fallback baseado no valor previsto de cada sugestão
                    actor_value = self.value_fn.predict(state_vector, stage, actor_choice)
                    value_value = self.value_fn.predict(state_vector, stage, value_choice)
                    chosen_executor = actor_choice if actor_value >= value_value else value_choice
                
                print(f"  Actor sugere: {actor_choice} | Value sugere: {value_choice} | Final: {chosen_executor}")
                
                # Simulação de leitura de resultado
                internal_score = 0.5
                res_path = f"executor_{'agent' if chosen_executor=='v1' else ('agent_v2' if chosen_executor=='v2' else 'llm')}/execution_result{'_v2' if chosen_executor=='v2' else ('_llm' if chosen_executor=='llm' else '')}.json"
                if os.path.exists(res_path):
                    with open(res_path, "r") as f:
                        res_data = json.load(f)
                        internal_score = self.internal_evaluate(chosen_executor, res_data, top)
                
                # 🔥 Feedback Actor-Critic
                # Critic avalia
                value = self.value_fn.predict(state_vector, stage, chosen_executor)
                advantage = internal_score - value

                # Critic aprende
                self.value_fn.update(state_vector, stage, chosen_executor, internal_score)

                # Actor aprende
                self.actor.update(stage, chosen_executor, advantage)
                print(f"Feedback Actor-Critic: Advantage={advantage:.4f}, Internal Score={internal_score}")
                
                # 1. Registrar Experiência
                experience = {
                    "timestamp": datetime.now().isoformat(),
                    "input_stage": top["stage"],
                    "executor": chosen_executor,
                    "internal_score": internal_score,
                    "coherence": top.get("coherence", 0.5),
                    "advantage": advantage
                }
                self.log_experience(experience)

                # 3. Exportar Estado Completo (Persistência da Camada 1)
                feedbacks = self.read_all_feedbacks()
                
                scored = []
                for f in feedbacks:
                    reward = compute_reward(
                        top["stage"],
                        f["executor"],
                        f["score"],
                        state_vector
                    )
                    scored.append({
                        **f,
                        "reward": reward
                    })

                if scored:
                    best = max(scored, key=lambda x: x["reward"])
                    best_score = best["reward"]
                    best_executor = best["executor"]
                    best_config = best.get("config", {})
                else:
                    best = {}
                    best_score = 0
                    best_executor = None
                    best_config = {}

                bridge_data = {
                    "agent": "zafira-psi0",
                    "timestamp": datetime.now().isoformat(),
                    "state_vector": state_vector,
                    "chosen_executor": chosen_executor,
                    "internal_score": internal_score,
                    "advantage": advantage,
                    "probabilities": actor_probs,
                    "best_decision": top,
                    "ranking": ranked,
                    "network_status": feedbacks,
                    "best_reward": best_score,
                    "best_executor": best_executor,
                    "value_predictions": predictions
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
