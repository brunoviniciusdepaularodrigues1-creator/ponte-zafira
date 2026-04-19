import json
import random
import numpy as np
import os


class EvolutionaryRouter:
    def __init__(self, agents, memory_path="agent_policy_v2.json"):
        self.agents = agents
        self.memory_path = memory_path
        self.policy = self._load_policy()
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
            "numeric":  {"score": 0.5, "count": 0},
            "llm":      {"score": 0.5, "count": 0}
        }

    def _save_policy(self):
        with open(self.memory_path, 'w') as f:
            json.dump(self.policy, f, indent=2)

    def get_preference(self, task_type):
        """
        N18 Passo 2: Retorna o tipo de agente preferido pela memória para o contexto.
        Usa o histórico de scores da política para ORIENTAR (não mandar) a seleção.
        Retorna None se não há preferência clara (scores muito próximos).
        """
        # Candidatos relevantes por tipo de tarefa
        candidates = {
            "symbolic": ["symbolic", "llm"],
            "numeric":  ["numeric", "symbolic"],
            "llm":      ["llm", "numeric"]
        }.get(task_type, list(self.policy.keys()))

        scores = {t: self.policy[t]["score"] for t in candidates}
        best  = max(scores, key=scores.get)
        worst = min(scores, key=scores.get)

        # Só retorna preferência se a diferença for significativa (> 0.05)
        if scores[best] - scores[worst] > 0.05:
            return best
        return None

    def select_agent(self, task):
        """
        Pipeline de seleção N18 Passo 2:
          state → actor → coherence_bias → memory_bias (0.05) → seleção final
        """
        # 1. Detecta tipo de tarefa
        task_type = self._detect_task_type(task)

        # 2. Actor distribution (baseado na política aprendida)
        agent_types = ["symbolic", "numeric", "llm"]
        probs = [self.policy[t]["score"] for t in agent_types]

        # 3. Coherence Bias — orienta por domínio estrutural
        bias = [0.0, 0.0, 0.0]
        if task_type == "symbolic":
            bias[0] = 0.4
        elif task_type == "numeric":
            bias[1] = 0.4
        else:
            bias[2] = 0.4

        # 4. Memory Bias (N18 Passo 2) — bônus leve baseado na memória acumulada
        # A memória orienta, não manda. Exploração e competição continuam vivas.
        MEMORY_BIAS = 0.05
        preferred = self.get_preference(task_type)
        memory_bias_vec = [0.0, 0.0, 0.0]
        if preferred is not None and preferred in agent_types:
            idx = agent_types.index(preferred)
            memory_bias_vec[idx] = MEMORY_BIAS

        # 5. Seleção Final (Amostragem Ponderada)
        combined_probs = np.array(probs) + np.array(bias) + np.array(memory_bias_vec)
        combined_probs = combined_probs / combined_probs.sum()

        selected_type = random.choices(agent_types, weights=combined_probs, k=1)[0]

        # Retorna o agente correspondente ao tipo selecionado
        for agent in self.agents:
            if agent.type == selected_type:
                return agent, combined_probs.tolist(), {
                    "task_type": task_type,
                    "preferred_by_memory": preferred,
                    "memory_bias_applied": preferred is not None
                }

        return self.agents[0], combined_probs.tolist(), {
            "task_type": task_type,
            "preferred_by_memory": None,
            "memory_bias_applied": False
        }

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
        alpha = 0.1
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

    agent, probs, meta = router.select_agent("x**2 - 4 = 0")
    print(f"Selected: {agent.name}, Probs: {probs}, Meta: {meta}")

    router.update_policy("symbolic", 0.9)
    print(f"Updated Policy: {router.policy}")
