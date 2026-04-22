import json
import random
import numpy as np
import os
import json


class InternalState:
    """
    N18 Passo 5 — Estado interno de desempenho recente.
    Mantém uma janela deslizante dos últimos 5 rewards para
    calcular a temperatura adaptativa de exploração.
    """

    def __init__(self, window=5):
        self.last_task   = None
        self.last_choice = None
        self.last_reward = None
        self.recent_rewards = []
        self.window = window

    def update(self, task, choice, reward):
        self.last_task   = task
        self.last_choice = choice
        self.last_reward = reward
        self.recent_rewards.append(reward)
        if len(self.recent_rewards) > self.window:
            self.recent_rewards.pop(0)

    def recent_average_reward(self):
        if not self.recent_rewards:
            return 0.5
        return sum(self.recent_rewards) / len(self.recent_rewards)

    def adaptive_temperature(self):
        """
        Regra de temperatura adaptativa:
          avg < 0.4  → explora mais  (temperatura alta: 0.9)
          avg > 0.7  → explora menos (temperatura baixa: 0.6)
          caso base  → temperatura padrão: 0.7
        """
        avg = self.recent_average_reward()
        if avg < 0.4:
            return 0.9
        elif avg > 0.7:
            return 0.6
        return 0.7

    def health_state(self):
        """
        N18 Passo 6 — Estado de saúde operacional explícito.
        Deriva um diagnóstico legível do desempenho recente:
          avg < 0.3  → critical   (sistema em crise, exploração máxima)
          avg < 0.5  → recovering (saíndo do buraco, ainda instavel)
          avg >= 0.5 → stable     (desempenho aceitável, exploração controlada)
        """
        avg = self.recent_average_reward()
        if avg < 0.3:
            return "critical"
        elif avg < 0.5:
            return "recovering"
        return "stable"


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
        # N18 Passo 8 — Memória de erro estrutural
        # Registra quantas vezes cada agente falhou (reward < 0.3) por categoria
        self.error_memory = {
            "symbolic": {},
            "numeric":  {},
            "llm":      {}
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

    def select_agent(self, task, temperature=None, health=None):
        """
        Pipeline de seleção N18 Passo 7:
          state → actor → coherence_bias → adaptive_memory_bias (health-aware) → seleção final

        N18 P7: memory_bias agora é adaptativo ao health_state:
          critical   → 0.08 (confia mais na memória, protege especialistas)
          recovering → 0.06 (cautela moderada)
          stable     → 0.05 (exploração normal)
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

        # 4. Adaptive Memory Bias (N18 Passo 7) — bônus sensível ao health_state
        # Quando o sistema está mal, confia mais na memória (protege especialistas).
        # Quando está estável, mantém exploração normal.
        if health == "critical":
            adaptive_memory_bias = 0.08
        elif health == "recovering":
            adaptive_memory_bias = 0.06
        else:
            adaptive_memory_bias = 0.05  # stable (padrão)

        preferred = self.get_preference(task_type)
        memory_bias_vec = [0.0, 0.0, 0.0]
        if preferred is not None and preferred in agent_types:
            idx = agent_types.index(preferred)
            memory_bias_vec[idx] = adaptive_memory_bias

        # 5. Temperatura Adaptativa (N18 Passo 5)
        # Se não fornecida externamente, usa a temperatura interna do estado
        if temperature is None:
            temperature = getattr(self, '_adaptive_temperature', 0.7)

        # Aplica temperatura: eleva probs à potência (1/T) para suavizar/aguçar
        combined_probs = np.array(probs) + np.array(bias) + np.array(memory_bias_vec)
        combined_probs = np.clip(combined_probs, 1e-8, None)
        # Softmax com temperatura
        scaled = combined_probs ** (1.0 / temperature)
        combined_probs = scaled / scaled.sum()

        selected_type = random.choices(agent_types, weights=combined_probs, k=1)[0]

        # Retorna o agente correspondente ao tipo selecionado
        for agent in self.agents:
            if agent.type == selected_type:
                return agent, combined_probs.tolist(), {
                    "task_type": task_type,
                    "preferred_by_memory": preferred,
                    "memory_bias_applied": preferred is not None,
                    "adaptive_temperature": temperature,
                    "adaptive_memory_bias": adaptive_memory_bias,
                    "health_state": health
                }

        return self.agents[0], combined_probs.tolist(), {
            "task_type": task_type,
            "preferred_by_memory": None,
            "memory_bias_applied": False,
            "adaptive_temperature": temperature,
            "adaptive_memory_bias": adaptive_memory_bias,
            "health_state": health
        }

    def _detect_task_type(self, task):
        """
        N18 Passo 3 — Classificador estrutural em ordem de prioridade.
        Evita falsos positivos de 'symbolic' para operações aritméticas puras.

        Ordem: explanation > numeric (explícito) > algebra (variável/equação) > numeric (puro) > llm
        """
        t = task.lower().strip()

        # 1. Explicação — prioridade máxima
        if any(kw in t for kw in ["explique", "explain", "descreva", "describe",
                                   "por que", "why", "como funciona", "how does",
                                   "o que é", "what is", "o que são"]):
            return "llm"

        # 2. Numérico explícito (palavras-chave que forçam numérico)
        if any(kw in t for kw in ["%", "calcule", "calculate", "quanto é",
                                   "dividido por", "divided by", "soma de",
                                   "sqrt", "sin", "cos", "log", "exp"]):
            return "numeric"

        # 3. Álgebra — equações ou expressões com variável
        has_variable = any(op in t for op in ["x", "y", "z", "**", "solve",
                                               "simplify", "resolva", "find x",
                                               "find y"])
        has_equals   = "=" in t
        if has_variable or has_equals:
            return "symbolic"

        # 4. Numérico puro — operação aritmética com dígitos, sem variável
        has_operator = any(op in t for op in ["+", "-", "*", "/"])
        has_digit    = any(ch.isdigit() for ch in t)
        if has_operator and has_digit:
            return "numeric"

        # 5. Fallback — LLM lida com o desconhecido
        return "llm"

    def register_error(self, task, agent_type, reward):
        """
        N18 Passo 8 — Registra falha estrutural quando reward < 0.3.
        Incrementa o contador de erros do agente na categoria da tarefa.
        """
        if reward < 0.3:
            category = self._detect_task_type(task)
            if category not in self.error_memory:
                self.error_memory[category] = {}
            if agent_type not in self.error_memory[category]:
                self.error_memory[category][agent_type] = 0
            self.error_memory[category][agent_type] += 1

    def get_error_penalty(self, task, agent_type):
        """
        N18 Passo 8 — Penalidade leve baseada em erros acumulados.
        Cresce 0.01 por erro, limitada a 0.05 (não bloqueia retorno).
        """
        category = self._detect_task_type(task)
        count = self.error_memory.get(category, {}).get(agent_type, 0)
        return min(0.05, count * 0.01)

    def update_policy(self, agent_type, reward, task=None):
        """
        Atualiza a política com base no reward recebido.
        N18 P8: registra erros estruturais se task for fornecida.
        """
        alpha = 0.1
        old_score = self.policy[agent_type]["score"]
        self.policy[agent_type]["score"] = old_score + alpha * (reward - old_score)
        self.policy[agent_type]["count"] += 1
        self._save_policy()
        # Registra erro estrutural se a tarefa for fornecida
        if task is not None:
            self.register_error(task, agent_type, reward)


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
