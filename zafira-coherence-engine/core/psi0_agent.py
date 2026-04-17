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
from core.action_space import ACTIONS
from core.psi0_coherence import CoherenceLayer
from core.dispatcher import execute
from core.psi0_semantic_reward import semantic_evaluate
from core.psi0_router import classify_task, get_strategy_bias
from core.meta_policy import MetaPolicy

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
        self.cycle = 0
        
        # Caminhos absolutos
        self.memory_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_memory.jsonl"))
        
        self.value_fn = ValueFunction()
        self.actor = PolicyActor()
        self.coherence = CoherenceLayer()
        self.meta = MetaPolicy()
        
        # Specialization Signal tracker
        self.specialization = {"A1": {"wins": 0, "total": 0}, "A2": {"wins": 0, "total": 0}, "A3": {"wins": 0, "total": 0}}

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
                self.cycle += 1
                print(f"\n--- Ciclo {self.cycle}: Aprendizado Cognitivo (Actor-Critic + Coherence) ---")
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

                # 🔥 CAMADA 5 Estável: Coherence Regulator
                stage = top["stage"]
                task_input = top["input"]
                
                # 🔥 Nível 7: Routing Contextual
                task_type = classify_task(task_input)
                strategy_bias = get_strategy_bias(task_type)
                print(f"Tipo de Tarefa: {task_type}")

                # 1. Actor sugere probabilidades
                raw_probs = self.actor.softmax(stage)
                
                # 2. Coherence aplica bias global + bias de estratégia (Nível 7)
                blended_probs = self.coherence.apply_contextual_bias(raw_probs, strategy_bias)
                
                # 3. Seleção final baseada nas probabilidades reguladas
                chosen_action = random.choices(
                    list(blended_probs.keys()),
                    weights=list(blended_probs.values())
                )[0]
                chosen_executor = ACTIONS[chosen_action]
                
                # 4. Critic avalia a expectativa (Baseline)
                value = self.value_fn.predict(state_vector, stage, chosen_action)
                
                print(f"  Probs Actor: {raw_probs}")
                print(f"  Probs Blended (Coherence + Strategy): {blended_probs}")
                print(f"  Actor escolheu ação: {chosen_action} → Executor: {chosen_executor} | Valor Previsto (Critic): {value:.4f}")
                
                # 🔥 Nível 7: Execução Real via Dispatcher
                output = execute(chosen_action, task_input)
                print(f"  Execução: {task_input} -> {output}")
                
                # 🔥 Nível 7: Semantic Reward (em vez de heurística fixa)
                # Como não temos o ground_truth em tempo real no modo treino genérico,
                # usamos uma heurística de sucesso do output para o internal_score,
                # mas em sistemas de benchmark usamos o semantic_evaluate.
                internal_score = 0.5
                if output is not None:
                    # No modo treino real, o internal_score viria da avaliação do resultado
                    internal_score = 0.8 
                else:
                    internal_score = 0.2
                
                # 🔥 Specialization Signal Tracker
                self.specialization[chosen_action]["total"] += 1
                if internal_score > 0.5:
                    self.specialization[chosen_action]["wins"] += 1
                
                # 5. Advantage
                advantage = internal_score - value

                # 6. Aprendizado Unificado
                self.value_fn.update(state_vector, stage, chosen_action, internal_score)
                self.actor.update(stage, chosen_action, advantage)
                self.coherence.update(chosen_action, advantage)
                self.meta.update(chosen_action, internal_score)
                
                print(f"  Feedback: Advantage={advantage:.4f} | Internal Score={internal_score}")
                
                                if self.cycle % 5 == 0:
                    print("  Meta Policy Scores:", self.meta.get_scores())
                    print("  Melhor ação atual:", self.meta.best_action())
                    print("  Specialization Signal:")
                    for action, stats in self.specialization.items():
                        rate = stats["wins"] / stats["total"] if stats["total"] > 0 else 0
                        print(f"    {action} ({ACTIONS[action]}): {stats['wins']}/{stats['total']} = {rate:.2f}")

                # Registrar Experiência
                experience = {
                    "timestamp": datetime.now().isoformat(),
                    "input_stage": top["stage"],
                    "action": chosen_action,
                    "executor": chosen_executor,
                    "internal_score": internal_score,
                    "coherence": top.get("coherence", 0.5),
                    "advantage": advantage,
                    "state_vector": state_vector,
                    "task_type": task_type
                }
                self.log_experience(experience)

                # Exportar Estado Completo
                feedbacks = self.read_all_feedbacks()
                
                bridge_data = {
                    "agent": "zafira-psi0",
                    "timestamp": datetime.now().isoformat(),
                    "state_vector": state_vector,
                    "chosen_action": chosen_action,
                    "chosen_executor": chosen_executor,
                    "internal_score": internal_score,
                    "advantage": advantage,
                    "raw_probabilities": raw_probs,
                    "blended_probabilities": blended_probs,
                    "best_decision": top,
                    "ranking": ranked,
                    "network_status": feedbacks,
                    "specialization": self.specialization,
                    "task_type": task_type
                }

                with open("bridge_interface.json.tmp", "w") as f:
                    json.dump(bridge_data, f, indent=2, ensure_ascii=False)
                os.replace("bridge_interface.json.tmp", "bridge_interface.json")
                
                print(f"Estado persistido no bridge.")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nPsi0Agent finalizado.")

if __name__ == "__main__":
    agent = Psi0Agent()
    agent.run()
