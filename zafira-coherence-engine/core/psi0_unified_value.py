"""
N16 — Unified Value Function (Integração Latente Total)
=======================================================
Consolida todos os sinais cognitivos do Zafira Coherence Engine
em um único vetor de estado unificado e uma função de valor global.

Módulos integrados:
  - psi0_state_encoder   → entropia, coerência, taxas históricas
  - psi0_reward          → reward contextual (estágio × executor)
  - psi0_value_function  → predição de valor por (estado, ação)
  - psi0_coherence       → política global de coerência
  - meta_policy          → efetividade histórica por ação
  - psi0_router          → bias de estratégia contextual

Objetivo:
  Todas as decisões passam por global_value(state_vector_unified),
  eliminando conflitos entre módulos e criando consenso interno.
"""

import math
import json
import os
from core.psi0_state_encoder import encode_state, simple_hash
from core.psi0_reward import compute_reward
from core.psi0_value_function import ValueFunction
from core.psi0_coherence import CoherenceLayer
from core.meta_policy import MetaPolicy
from core.psi0_router import classify_task, get_strategy_bias


# Mapeamento de executores para índices no espaço latente
EXECUTOR_INDEX = {"A1": 0, "A2": 1, "A3": 2, "v1": 0, "v2": 1, "llm": 2}
EXECUTOR_NAMES = ["A1", "A2", "A3"]


class UnifiedValueFunction:
    """
    Função de Valor Unificada — N16.

    Constrói um vetor de estado enriquecido (9 dimensões) combinando:
      [0] stage_hash         — identidade ontológica do momento
      [1] text_len           — complexidade do input
      [2] llm_rate           — efetividade histórica do LLM
      [3] v1_rate            — efetividade histórica do V1
      [4] v2_rate            — efetividade histórica do V2
      [5] entropy            — incerteza da política atual
      [6] prediction_error   — erro de predição do ciclo anterior
      [7] curiosity_score    — surpresa / novidade do estado
      [8] meta_score         — efetividade média da meta-política

    A função global_value() combina todos os sinais em um único escalar
    que orienta a decisão final do sistema.
    """

    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "unified_value_memory.json")
        self.value_fn = ValueFunction()
        self.coherence = CoherenceLayer()
        self.meta = MetaPolicy()
        self._last_prediction = {}   # executor → última predição
        self._last_reward = {}       # executor → último reward real
        self.W = self._load_weights()

    def _load_weights(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        # 9 pesos inicializados com valor neutro
        return {"weights": [0.1] * 9, "cycles": 0}

    def _save_weights(self):
        with open(self.path, "w") as f:
            json.dump(self.W, f, indent=2)

    # ------------------------------------------------------------------
    # Construção do Vetor de Estado Unificado
    # ------------------------------------------------------------------

    def _compute_entropy(self):
        """Entropia de Shannon da política de coerência global."""
        probs = list(self.coherence.global_policy.values())
        entropy = -sum(p * math.log(p + 1e-9) for p in probs)
        # Normaliza para [0, 1] usando log(n) como máximo
        return round(entropy / math.log(len(probs) + 1e-9), 4)

    def _compute_prediction_error(self, executor):
        """Erro de predição do ciclo anterior para o executor dado."""
        pred = self._last_prediction.get(executor, 0.5)
        real = self._last_reward.get(executor, 0.5)
        return round(abs(real - pred), 4)

    def _compute_curiosity(self, stage, input_text):
        """
        Surpresa / novidade: quanto o estado atual difere do esperado.
        Usa o hash do stage + comprimento do texto como proxy de novidade.
        """
        stage_h = simple_hash(stage) / 1000.0
        text_h = simple_hash(input_text[:20]) / 1000.0
        # Distância simples do estado "neutro" (0.5, 0.5)
        curiosity = math.sqrt((stage_h - 0.5) ** 2 + (text_h - 0.5) ** 2)
        return round(min(curiosity, 1.0), 4)

    def _compute_meta_score(self):
        """Efetividade média da meta-política."""
        scores = self.meta.get_scores()
        return round(sum(scores.values()) / len(scores), 4)

    def build_unified_state(self, stage, input_text, history_stats=None, executor="v1"):
        """
        Constrói o vetor de estado unificado de 9 dimensões.
        Este é o único vetor que o sistema usa para tomar decisões.
        """
        history_stats = history_stats or {}
        base = encode_state(stage, input_text, history_stats)  # 5 dims

        entropy = self._compute_entropy()
        pred_error = self._compute_prediction_error(executor)
        curiosity = self._compute_curiosity(stage, input_text)
        meta_score = self._compute_meta_score()

        unified = base + [entropy, pred_error, curiosity, meta_score]
        return [round(v, 4) for v in unified]

    # ------------------------------------------------------------------
    # Função de Valor Global
    # ------------------------------------------------------------------

    def global_value(self, unified_state, executor):
        """
        Calcula o valor global do par (estado_unificado, executor).
        Esta é a função única que orienta todas as decisões do sistema.
        """
        exec_idx = EXECUTOR_INDEX.get(executor, 0)
        exec_one_hot = [1.0 if i == exec_idx else 0.0 for i in range(3)]
        x = unified_state[:9] + exec_one_hot  # 12 dims total

        W = self.W["weights"]
        # Padding se necessário
        while len(W) < len(x):
            W.append(0.1)
        self.W["weights"] = W[:len(x)]

        # Produto interno normalizado
        norm = math.sqrt(sum(xi ** 2 for xi in x)) + 1e-8
        x_norm = [xi / norm for xi in x]
        value = sum(w * xi for w, xi in zip(W, x_norm))
        return round(value, 4)

    def select_best_executor(self, unified_state, stage, available_executors=None):
        """
        Seleciona o melhor executor baseado na Unified Value Function.
        Substitui todas as heurísticas anteriores por consenso interno.
        """
        available = available_executors or ["v1", "v2", "llm"]
        scores = {}
        for exe in available:
            raw_value = self.global_value(unified_state, exe)
            contextual_reward = compute_reward(stage, exe, 0.5)
            # Consenso: 70% valor aprendido + 30% reward contextual
            scores[exe] = round(0.7 * raw_value + 0.3 * contextual_reward, 4)

        best = max(scores, key=scores.get)
        return best, scores

    # ------------------------------------------------------------------
    # Atualização de Pesos (Aprendizado)
    # ------------------------------------------------------------------

    def update(self, unified_state, executor, reward, lr=0.03):
        """
        Atualiza os pesos da Unified Value Function via gradiente.
        Também atualiza os módulos dependentes (coherence, meta, value_fn).
        """
        exec_idx = EXECUTOR_INDEX.get(executor, 0)
        exec_one_hot = [1.0 if i == exec_idx else 0.0 for i in range(3)]
        x = unified_state[:9] + exec_one_hot

        W = self.W["weights"]
        while len(W) < len(x):
            W.append(0.1)

        norm = math.sqrt(sum(xi ** 2 for xi in x)) + 1e-8
        x_norm = [xi / norm for xi in x]
        prediction = sum(w * xi for w, xi in zip(W, x_norm))
        error = reward - prediction

        # Atualização com clamp para estabilidade
        new_W = [max(-2.0, min(2.0, w + lr * error * xi)) for w, xi in zip(W, x_norm)]
        self.W["weights"] = new_W
        self.W["cycles"] = self.W.get("cycles", 0) + 1
        self._save_weights()

        # Registra predição para cálculo de erro no próximo ciclo
        self._last_prediction[executor] = prediction
        self._last_reward[executor] = reward

        # Propaga aprendizado para módulos dependentes
        action = EXECUTOR_NAMES[exec_idx]
        self.coherence.update(action, reward, lr=0.01)
        self.meta.update(action, reward)

        return round(prediction, 4), round(error, 4)

    def get_telemetry(self, unified_state, executor, reward):
        """Retorna telemetria completa do ciclo N16."""
        return {
            "unified_state": unified_state,
            "global_value": self.global_value(unified_state, executor),
            "entropy": unified_state[5] if len(unified_state) > 5 else None,
            "prediction_error": unified_state[6] if len(unified_state) > 6 else None,
            "curiosity": unified_state[7] if len(unified_state) > 7 else None,
            "meta_score": unified_state[8] if len(unified_state) > 8 else None,
            "reward": reward,
            "coherence_dominant": self.coherence.get_dominant(),
            "meta_best": self.meta.best_action(),
            "total_cycles": self.W.get("cycles", 0)
        }
