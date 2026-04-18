import time
import os
import sys
import json
import random
import math
import numpy as np
from datetime import datetime

# 🔥 Nível 15: Reprodutibilidade Científica (Determinismo)
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

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
from core.shadow_policy import ShadowPolicy
from core.curiosity_engine import CuriosityEngine
from core.world_model import WorldModel

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
        
        # Nível 11: Shadow Mode e Auto-Modificação
        self.shadow = ShadowPolicy(self.meta)
        self.performance_history = []
        
        # Nível 12: Curiosity e Goal Generation
        self.curiosity = CuriosityEngine(bound=0.05)
        self.synthetic_goals = []
        
        # Nível 13: World Model
        self.world_model = WorldModel(state_dim=10)
        
        # Specialization Signal tracker
        self.specialization = {"A1": {"wins": 0, "total": 0}, "A2": {"wins": 0, "total": 0}, "A3": {"wins": 0, "total": 0}}

    def compute_entropy(self, probs):
        """Calcula a entropia de Shannon para uma distribuição de probabilidades."""
        p_values = np.array(list(probs.values()))
        p_values = p_values[p_values > 0] # Evitar log(0)
        if len(p_values) <= 1: return 0.0
        return -np.sum(p_values * np.log2(p_values))

    def log_experience(self, experience):
        """Salva a experiência estruturada no log de memória."""
        with open(self.memory_file, "a") as f:
            f.write(json.dumps(experience, ensure_ascii=False) + "\n")

    def run(self, max_cycles=None):
        print(f"Zafira Coherence Engine: Psi0Agent N15 (Architecture Consolidation) Iniciado... [SEED: {SEED}]")
        try:
            while True:
                if max_cycles and self.cycle >= max_cycles:
                    print(f"🏁 Limite de {max_cycles} ciclos atingido.")
                    break
                    
                self.cycle += 1
                print(f"\n--- Ciclo {self.cycle}: Unified Pipeline (N15) ---")
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
                
                # 🔥 Nível 7/10: Routing Contextual
                task_input = top["input"]
                task_type = classify_task(task_input)
                strategy_bias = get_strategy_bias(task_type)
                print(f"Tipo de Tarefa: {task_type}")

                # 🔥 Nível 14: Long-Horizon Strategy (Planejamento de Sequência)
                # O sistema avalia trajetórias de 3 passos à frente
                planning_depth = 3
                trajectories = {}
                
                # Simplificado: Testa sequências onde a primeira ação varia
                for first_action in ACTIONS.keys():
                    # Gera sequências plausíveis (ex: repetir a mesma ação ou alternar)
                    # Para o N14, focamos na melhor primeira ação baseada no futuro
                    seq = [first_action] * planning_depth
                    future_reward = self.world_model.simulate_sequence(state_vector, seq)
                    trajectories[first_action] = future_reward / planning_depth
                
                # 1. Actor e Coherence sugerem probabilidades
                raw_probs = self.actor.softmax(top["stage"])
                
                # Nível 12, 13 & 14: Curiosidade + Antecipação + Estratégia
                curiosity_bonus = self.curiosity.get_curiosity_signal(task_type)
                # O bias agora é estratégico (longo prazo)
                strategy_bias_n14 = {k: trajectories[k] * 0.3 for k in trajectories}
                
                blended_probs = self.coherence.apply_contextual_bias(raw_probs, strategy_bias + curiosity_bonus)
                # Blend final com foco estratégico
                for a in blended_probs:
                    blended_probs[a] = (blended_probs[a] * 0.7) + (strategy_bias_n14.get(a, 0) * 0.3)

                # 🔥 Nível 10.5: Adaptive Entropy Control
                # Calculamos a entropia do blend atual (Intuição/Coerência)
                current_entropy = self.compute_entropy(blended_probs)
                
                # Lógica de Modulação Adaptativa
                if current_entropy > 0.7:
                    # Sistema muito indeciso → Força especialização (MetaPolicy ganha peso)
                    meta_weight = 0.5
                    coherence_weight = 0.5
                    status_incerteza = "ALTA (Forçando Especialização)"
                elif current_entropy < 0.4:
                    # Sistema muito rígido → Força exploração (Coerência/Intuição ganha peso)
                    meta_weight = 0.2
                    coherence_weight = 0.8
                    status_incerteza = "BAIXA (Forçando Exploração)"
                else:
                    # Zona Ideal (0.4 - 0.7)
                    meta_weight = 0.3
                    coherence_weight = 0.7
                    status_incerteza = "IDEAL"

                print(f"Entropia Atual: {current_entropy:.4f} | Estado: {status_incerteza}")
                print(f"Modulação: Coherence={coherence_weight} | MetaPolicy={meta_weight}")

                # 2. MetaPolicy scores (Experiência)
                meta_scores, _ = self.meta.get_scores()
                total_meta_score = sum(meta_scores.values())
                meta_probs = {k: v / total_meta_score if total_meta_score > 0 else 1/len(meta_scores) for k, v in meta_scores.items()}

                # 3. Blend Adaptativo Final
                final_probs = {}
                for action in blended_probs:
                    final_probs[action] = (coherence_weight * blended_probs[action]) + (meta_weight * meta_probs.get(action, 0))
                
                # Normalização final
                total_final = sum(final_probs.values())
                final_probs = {k: v / total_final for k, v in final_probs.items()}

                # 4. Seleção e Execução
                chosen_action = random.choices(list(final_probs.keys()), weights=list(final_probs.values()))[0]
                chosen_executor = ACTIONS[chosen_action]
                output = execute(chosen_action, task_input)
                
                # 5. Avaliação e Aprendizado (Simplificado para o loop principal)
                internal_score = 0.8 if output and "error" not in str(output).lower() else 0.2
                advantage = internal_score - self.value_fn.predict(state_vector, top["stage"], chosen_action)

                self.value_fn.update(state_vector, top["stage"], chosen_action, internal_score)
                self.actor.update(top["stage"], chosen_action, advantage)
                self.coherence.update(chosen_action, advantage)
                self.meta.update(chosen_action, internal_score)
                
                # Nível 13: Atualizar World Model
                # Simulamos um "next_state" para o update (simplificado)
                next_state_sim = encode_state(top.get("stage"), "next", history_stats)
                pred_error = self.world_model.update(state_vector, chosen_action, next_state_sim, internal_score)
                
                # Nível 12: Atualizar Curiosity Engine
                surprise = self.curiosity.measure_surprise(task_type, internal_score)
                
                # Nível 11: Atualizar Shadow Mode e Verificar Promoção
                self.shadow.update_both(chosen_action, internal_score, is_shadow_choice=False)
                self.performance_history.append(internal_score)
                
                # Se a performance cair drasticamente (> 30% abaixo da média), ativa rollback
                if len(self.performance_history) > 10:
                    avg_perf = np.mean(self.performance_history[-10:])
                    if internal_score < avg_perf * 0.7:
                        print("⚠️ Rollback Ativado: Queda de performance detectada!")
                        self.meta.exploration_boost = 0.3 # Reverte para valor estável
                
                if self.shadow.evaluate_promotion():
                    print("🚀 Promoção Nível 11: Shadow Policy provou ser superior!")
                    new_params = self.shadow.get_mutated_params()
                    self.meta.entropy_threshold = new_params["entropy_threshold"]
                    self.meta.exploration_boost = new_params["exploration_boost"]
                    # Resetar shadow para novo ciclo de mutação
                    self.shadow = ShadowPolicy(self.meta)
                
                # 🔥 Nível 15: Telemetria Total (Auditoria Científica)
                final_entropy_val = self.compute_entropy(final_probs)
                avg_pred_error = self.world_model.get_avg_error()
                
                # Logs e Persistência
                experience = {
                    "cycle": self.cycle,
                    "timestamp": datetime.now().isoformat(),
                    "telemetry": {
                        "entropy_initial": current_entropy,
                        "entropy_final": final_entropy_val,
                        "meta_weight": meta_weight,
                        "coherence_weight": coherence_weight,
                        "prediction_error": pred_error,
                        "avg_prediction_error": avg_pred_error,
                        "surprise_val": surprise
                    },
                    "decision": {
                        "task_type": task_type,
                        "chosen_action": chosen_action,
                        "score": internal_score
                    },
                    "n15_consolidated": True
                }
                self.log_experience(experience)
                
                print(f"Ação: {chosen_action} | Score: {internal_score}")
                print(f"Telemetria [H: {final_entropy_val:.4f} | Err: {avg_pred_error:.4f} | Surp: {surprise:.4f}]")
                time.sleep(self.interval)

        except KeyboardInterrupt:
            print("\nPsi0Agent finalizado.")

if __name__ == "__main__":
    agent = Psi0Agent()
    agent.run()
