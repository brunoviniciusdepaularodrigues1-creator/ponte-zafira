import time
import os
import sys
import json
import random
import math
from datetime import datetime
import numpy as np

def calc_entropy(probs):
    p = np.array(list(probs.values()))
    p = p[p > 0]
    return -np.sum(p * np.log(p)) if len(p) > 0 else 0.0


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
from core.latent_encoder import LatentEncoder
from core.psi0_unified_value import UnifiedValueFunction

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
        # 🔥 N16: Unified Value Function — espaço latente unificado
        self.uvf = UnifiedValueFunction()
        
        # Specialization Signal tracker
        self.specialization = {"A1": {"wins": 0, "total": 0}, "A2": {"wins": 0, "total": 0}, "A3": {"wins": 0, "total": 0}}
        self.encoder = LatentEncoder(input_dim=5, latent_dim=2)
        self.prediction_errors = []

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
                
                # 🔥 N16.5: Latent Encoding
                latent = self.encoder.encode(np.array(state_vector))
                print(f"  Estado Latente (Encoder): {latent}")

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

                # 🔥 Nível 8: MetaPolicy influencia a decisão do router
                meta_scores = self.meta.get_scores()
                # Normalizar meta_scores para somar 1
                total_meta_score = sum(meta_scores.values())
                meta_probs = {k: v / total_meta_score if total_meta_score > 0 else 1/len(meta_scores) for k, v in meta_scores.items()}

                # Blend final: 0.7 para o blend atual (coerência/actor) + 0.3 para meta_policy scores
                final_probs = {}
                for action in blended_probs:
                    final_probs[action] = (0.7 * blended_probs[action]) + (0.3 * meta_probs.get(action, 0))
                
                # Normalizar final_probs para garantir que somem 1
                total_final_probs = sum(final_probs.values())
                if total_final_probs > 0:
                    final_probs = {k: v / total_final_probs for k, v in final_probs.items()}
                else:
                    # Fallback para distribuição uniforme se todas as probabilidades forem zero
                    final_probs = {k: 1/len(final_probs) for k in final_probs}

                # 🔥 N18 Passo 2: Injetar preferência da memória do MetaOrchestrator como viés leve
                preferred = self.meta.get_preference(task_type)
                if preferred is not None and preferred in final_probs:
                    memory_bias = 0.05
                    final_probs[preferred] += memory_bias
                    # Re-normalizar após aplicar o viés
                    total_final_probs = sum(final_probs.values())
                    final_probs = {k: v / total_final_probs for k, v in final_probs.items()}

                # 3. Seleção final baseada nas probabilidades reguladas
                chosen_action = random.choices(
                    list(final_probs.keys()),
                    weights=list(final_probs.values())
                )[0]
                

                chosen_executor = ACTIONS[chosen_action]
                
                # 4. Critic avalia a expectativa (Baseline)
                value = self.value_fn.predict(latent, stage, chosen_action)
                alpha = 0.05
                entropy = calc_entropy(final_probs)
                value = value - alpha * entropy
                
                print(f"  Probs Actor: {raw_probs}")
                print(f"  Probs Blended (Coherence + Strategy): {blended_probs}")
                print(f"  Probs MetaPolicy: {meta_probs}")
                print(f"  Probs Finais (Blended + MetaPolicy): {final_probs}")
                

                
                print(f"  Entropia: {calc_entropy(final_probs):.4f}")
                print(f"  Actor escolheu ação: {chosen_action} → Executor: {chosen_executor} | Valor Previsto (Critic): {value:.4f}")
                
                # 🔥 Nível 7: Execução Real via Dispatcher
                output = execute(chosen_action, task_input)
                print(f"  Execução: {task_input} -> {output}")
                
                # 🔥 Nível 7: Semantic Reward
                internal_score = 0.1 # Default para falha
                
                # Avaliação mais granular baseada no tipo de agente e na qualidade do output
                if chosen_action == "A1": # Symbolic Solver
                    if output is not None and ("[" in str(output) or "I" in str(output) or "sqrt" in str(output)) and "error" not in str(output).lower():
                        internal_score = 0.9
                    elif output is not None and len(str(output)) > 0 and "error" not in str(output).lower():
                        internal_score = 0.7
                    else:
                        internal_score = 0.2
                elif chosen_action == "A2": # Numeric Solver
                    try:
                        if isinstance(output, str) and output.startswith("[") and output.endswith("]"):
                            nums = [float(s.strip()) for s in output[1:-1].split(',') if s.strip()]
                            if nums: internal_score = 0.9
                        elif float(output) is not None: 
                            internal_score = 0.9
                        else:
                            internal_score = 0.2
                    except (ValueError, TypeError):
                        internal_score = 0.2
                elif chosen_action == "A3": # LLM Solver
                    if output is not None and len(str(output)) > 5 and "error" not in str(output).lower() and "None" not in str(output):
                        internal_score = 0.8
                    else:
                        internal_score = 0.2
                
                if output == "curto" or "falha" in str(output).lower():
                    internal_score = 0.1
                
                # 🔥 Specialization Signal Tracker
                self.specialization[chosen_action]["total"] += 1
                if internal_score > 0.5:
                    self.specialization[chosen_action]["wins"] += 1
                
                # 5. Advantage
                advantage = internal_score - value

                # 6. Aprendizado Unificado
                self.value_fn.update(latent, stage, chosen_action, internal_score)
                self.actor.update(stage, chosen_action, advantage)
                self.coherence.update(chosen_action, advantage)
                self.meta.update(task_type, chosen_action, internal_score)
                self.encoder.update(np.array(state_vector), latent, advantage)
                self.prediction_errors.append(abs(advantage))
                
                # 🔥 N16: Unified Value Function Integration
                unified_state = self.uvf.build_unified_state(stage, task_input, history_stats, chosen_executor)
                uvf_pred, uvf_error = self.uvf.update(unified_state, chosen_executor, internal_score)
                print(f"  N16 UVF: pred={uvf_pred:.4f} | erro={uvf_error:.4f}")
                
                print(f"  Feedback: Advantage={advantage:.4f} | Internal Score={internal_score}")
                
                if self.cycle % 5 == 0:
                    print("  Meta Policy Scores:", self.meta.get_scores())
                    print("  Melhor ação atual:", self.meta.best_action())
                    print(f"  Entropia atual: {calc_entropy(final_probs):.4f}")
                    avg_prediction_error = np.mean(self.prediction_errors[-5:]) if len(self.prediction_errors) > 0 else 0.0
                    print(f"  Prediction error médio (últimos 5 ciclos): {avg_prediction_error:.4f}")
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
                    "latent_representation": latent.tolist(),
                    "task_type": task_type
                }
                self.log_experience(experience)

                # Exportar Estado Completo
                feedbacks = self.read_all_feedbacks()
                
                bridge_data = {
                    "agent": "zafira-psi0",
                    "timestamp": datetime.now().isoformat(),
                    "state_vector": state_vector,
                    "latent_representation": latent.tolist(),
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
                    "meta_policy_stats": self.meta.stats,
                    "latent_encoder_weights": self.encoder.W.tolist(),
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
