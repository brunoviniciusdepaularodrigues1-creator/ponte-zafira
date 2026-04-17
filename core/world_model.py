import numpy as np
import json

class WorldModel:
    """
    World Model Nível 13: Constrói um modelo interno do ambiente.
    Prediz o próximo estado e a recompensa esperada para simulação interna.
    """
    def __init__(self, state_dim=10, learning_rate=0.05):
        self.state_dim = state_dim
        self.lr = learning_rate
        # Transição: P(s' | s, a) - Simplificado para mapeamento linear
        self.transition_matrix = {
            "A1": np.eye(state_dim),
            "A2": np.eye(state_dim),
            "A3": np.eye(state_dim)
        }
        # Recompensa: R(s, a)
        self.reward_model = {
            "A1": np.zeros(state_dim),
            "A2": np.zeros(state_dim),
            "A3": np.zeros(state_dim)
        }
        self.prediction_errors = []

    def predict(self, state, action):
        """Prediz o próximo estado e recompensa."""
        if action not in self.transition_matrix:
            return state, 0.5
        
        # Predição linear simples
        next_state = np.dot(self.transition_matrix[action], state)
        # Normalização para manter no espaço de estado
        next_state = next_state / (np.linalg.norm(next_state) + 1e-9)
        
        expected_reward = np.dot(self.reward_model[action], state)
        expected_reward = 1.0 / (1.0 + np.exp(-expected_reward)) # Sigmoid
        
        return next_state, expected_reward

    def update(self, state, action, next_state, actual_reward):
        """Treina o modelo interno com dados reais."""
        pred_state, pred_reward = self.predict(state, action)
        
        # Erro de predição (Surpresa do World Model)
        state_error = np.linalg.norm(next_state - pred_state)
        reward_error = abs(actual_reward - pred_reward)
        self.prediction_errors.append(reward_error)
        
        # Atualização Gradiente (Simplificada)
        # Ajusta o modelo de recompensa
        self.reward_model[action] += self.lr * (actual_reward - pred_reward) * state
        
        # Ajusta a matriz de transição (Delta rule)
        state_diff = (next_state - pred_state).reshape(-1, 1)
        state_input = state.reshape(1, -1)
        self.transition_matrix[action] += self.lr * np.dot(state_diff, state_input)
        
        return reward_error

    def get_avg_error(self):
        if not self.prediction_errors: return 1.0
        return np.mean(self.prediction_errors[-50:])
