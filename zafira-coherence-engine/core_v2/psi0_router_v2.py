import json
import random
import numpy as np
import os

class EvolutionaryRouter:
    def __init__(self, agents, memory_path="agent_policy_v2.json"):
        self.agents = agents
        self.memory_path = memory_path
        self.policy = self._load_policy()
        self.temperature = 0.7  # Ajuste N17.2: Reduzir ruído sem matar exploração
        self.coherence_bias = {
            "symbolic": 0.33,
            "numeric": 0.33,
            "llm": 0.34
        }

    def _load_policy(self):
        if os.path.exists(self.memory_path):
            with open(self.memory_path, 'r') as f:
                return json.load(f)
        return {
            "symbolic": {"score": 0.5, "count": 0},
            "numeric": {"score": 0.5, "count": 0},
            "llm": {"score": 0.5, "count": 0}
        }

    def _save_policy(self):
        with open(self.memory_path, 'w') as f:
            json.dump(self.policy, f, indent=2)

    def select_agent(self, task):
        """
        state -> actor -> distribuição sobre agentes (A1/A2/A3) -> coherence bias -> seleção final
        """
        # 1. Encode state (simplificado: detecta tipo de tarefa)
        task_type = self._detect_task_type(task)
        
        # 2. Actor distribution (baseado na política aprendida)
        probs = []
        agent_types = ["symbolic", "numeric", "llm"]
        for t in agent_types:
            # P(A) = score_A / sum(scores)
            probs.append(self.policy[t]["score"])
        
        # 3. Coherence Bias (Coherence 2.0)
        # Se problema é simbólico -> p(A1) ↑, numérico -> p(A2) ↑, ambíguo -> p(A3) ↑
        bias = [0.0, 0.0, 0.0]
        if task_type == "symbolic":
            bias[0] = 0.4
        elif task_type == "numeric":
            bias[1] = 0.4
        else:
            bias[2] = 0.4
            
        # 4. Seleção Final (Softmax com Temperatura ou Amostragem Ponderada)
        # Aplicando temperatura para suavizar/acentuar a distribuição
        combined_scores = np.array(probs) + np.array(bias)
        
        # Softmax com temperatura: exp(score/T) / sum(exp(score/T))
        exp_scores = np.exp(combined_scores / self.temperature)
        combined_probs = exp_scores / exp_scores.sum()
        
        selected_type = random.choices(agent_types, weights=combined_probs, k=1)[0]
        
        # Retorna o agente correspondente ao tipo selecionado
        for agent in self.agents:
            if agent.type == selected_type:
                return agent, combined_probs.tolist()
        
        return self.agents[0], combined_probs.tolist()

    def _detect_task_type(self, task):
        task = task.lower()
        if any(op in task for op in ["**", "x", "y", "z", "solve", "simplify"]):
            return "symbolic"
        if any(op in task for op in ["sqrt", "sin", "cos", "log", "exp"]) or any(c.isdigit() for c in task):
            return "numeric"
        return "llm"

    def update_policy(self, agent_type, reward):
        """
        Atualiza a política com base no reward recebido.
        """
        alpha = 0.1 # Taxa de aprendizado
        old_score = self.policy[agent_type]["score"]
        self.policy[agent_type]["score"] = old_score + alpha * (reward - old_score)
        self.policy[agent_type]["count"] += 1
        self._save_policy()

if __name__ == "__main__":
    from agents.a1_symbolic import SymbolicSolver
    from agents.a2_numeric import NumericSolver
    from agents.a3_llm import LLMSolver
    
    agents = [SymbolicSolver(), NumericSolver(), LLMSolver()]
    router = EvolutionaryRouter(agents)
    
    agent, probs = router.select_agent("x**2 - 4 = 0")
    print(f"Selected: {agent.name}, Probs: {probs}")
    
    router.update_policy("symbolic", 0.9)
    print(f"Updated Policy: {router.policy}")
