import json
import time
import os
import copy
from agents.a1_symbolic import SymbolicSolver
from agents.a2_numeric import NumericSolver
from agents.a3_llm import LLMSolver
from judge.adversarial_judge import AdversarialJudge
from core_v2.psi0_router_v2 import EvolutionaryRouter

class ZafiraCoherenceEngineV75:
    def __init__(self):
        self.a1 = SymbolicSolver()
        self.a2 = NumericSolver()
        self.a3 = LLMSolver()
        self.agents = [self.a1, self.a2, self.a3]
        self.judge = AdversarialJudge()
        self.router = EvolutionaryRouter(self.agents)
        self.history_path = "agent_evolution_v75_log.txt"

    def run_task(self, task):
        """
        for task: state = encode(task), A1/A2/A3 = solve(task), judge = compare(A1, A2, A3), 
        reward = judge.score, actor.update(reward), value_fn.update(reward), 
        coherence.update(reward), log experience
        """
        print(f"\n--- Processando Tarefa: {task} ---")
        
        # Capture pre-policy state for observability
        pre_policy = copy.deepcopy(self.router.policy)
        
        # 1. Seleção do Agente Principal (Router Evolutivo)
        selected_agent, probs = self.router.select_agent(task)
        print(f"Router selecionou: {selected_agent.name} (Probs: {probs})")
        
        # 2. Execução de todos os agentes (Competição/Self-Play)
        results = {}
        for agent in self.agents:
            start_time = time.time()
            res = agent.solve(task)
            res["time"] = round(time.time() - start_time, 4)
            results[agent.name] = res
            print(f"Agente {agent.name} respondeu: {res['result']}")
            
        # 3. Avaliação pelo Juiz Adversarial
        evaluation = self.judge.evaluate(task, results)
        final_scores = evaluation["final_scores"]
        print(f"Juiz avaliou scores: {final_scores}")
        
        # 4. Cálculo do Reward (Nova Função de Reward)
        # reward = correctness + agent_specialization_bonus + disagreement_resolution_bonus - hallucination_penalty
        rewards = self._calculate_rewards(task, results, evaluation, selected_agent)
        print(f"Rewards calculados: {rewards}")
        
        # 5. Atualização da Política (Router Evolutivo)
        for agent in self.agents:
            self.router.update_policy(agent.type, rewards[agent.name])
            
        # Capture post-policy state for observability
        post_policy = copy.deepcopy(self.router.policy)
            
        # 6. Log Experience
        self._log_experience(task, results, evaluation, rewards, selected_agent, probs, pre_policy, post_policy)
        
        return {
            "task": task,
            "selected_agent": selected_agent.name,
            "results": results,
            "evaluation": evaluation,
            "rewards": rewards
        }

    def _calculate_rewards(self, task, results, evaluation, selected_agent):
        """
        reward = correctness + agent_specialization_bonus + disagreement_resolution_bonus - hallucination_penalty
        """
        rewards = {}
        final_scores = evaluation["final_scores"]
        agreement = evaluation["metrics"]["agreement"]
        
        for name, res in results.items():
            # Correctness (baseado no score do juiz)
            correctness = final_scores[name]
            
            # Agent Specialization Bonus
            # Se o agente selecionado pelo router for o que teve o melhor score, ganha bônus
            specialization_bonus = 0.1 if name == selected_agent.name and final_scores[name] == max(final_scores.values()) else 0.0
            
            # Disagreement Resolution Bonus
            # Se houve desacordo (agreement baixo) mas o agente manteve alta acurácia, ganha bônus
            disagreement_resolution_bonus = 0.1 if agreement < 0.5 and final_scores[name] > 0.8 else 0.0
            
            # Hallucination Penalty
            # Se o status for erro ou o resultado for vazio/nonsense
            hallucination_penalty = 0.5 if res["status"] == "error" or not res["result"] else 0.0
            
            reward = correctness + specialization_bonus + disagreement_resolution_bonus - hallucination_penalty
            
            # N17.2 Etapa 10: Bônus de Domínio para coerência contextual
            domain_bonus = 0.0
            task_lower = task.lower()
            agent_type_code = name.split(" - ")[0].lower() # a1, a2, a3
            
            if "x" in task_lower or "=" in task_lower:
                if agent_type_code == "a1": domain_bonus = 0.05
            elif "%" in task_lower or "calcule" in task_lower:
                if agent_type_code == "a2": domain_bonus = 0.05
            elif "explique" in task_lower:
                if agent_type_code == "a3": domain_bonus = 0.05
            
            reward = reward + domain_bonus
            
            # N17.2 Etapa 8: Penalidade de Dominância para evitar monocultura
            mapped_type = {"a1": "symbolic", "a2": "numeric", "a3": "llm"}.get(agent_type_code)
            dominance_penalty = 0.0
            if mapped_type and self.router.policy[mapped_type]["score"] > 0.7:
                dominance_penalty = 0.05
                
            reward = reward - dominance_penalty
            rewards[name] = round(max(0, reward), 4)
            
        return rewards

    def _log_experience(self, task, results, evaluation, rewards, selected_agent, probs, pre_policy, post_policy):
        log_entry = {
            "timestamp": time.time(),
            "task": task,
            "selected_agent": selected_agent.name,
            "selected_agent_type": selected_agent.type,
            "selection_probs": probs,
            "final_scores": evaluation["final_scores"],
            "rewards": rewards,
            "agreement": evaluation["metrics"]["agreement"],
            "decision_margin": evaluation["metrics"]["decision_margin"],
            "pre_policy": pre_policy,
            "post_policy": post_policy
        }
        with open(self.history_path, "a") as f:
            f.write(json.dumps(log_entry) + "\n")

if __name__ == "__main__":
    engine = ZafiraCoherenceEngineV75()
    engine.run_task("x**2 - 36 = 0")
    engine.run_task("Resolva: 4x - 12 = 0")
    engine.run_task("Calcule 18% de 250")
    engine.run_task("Qual é 144 dividido por 12?")
    engine.run_task("Explique gravidade em uma frase simples")
    engine.run_task("Explique o que é porcentagem em uma frase")
