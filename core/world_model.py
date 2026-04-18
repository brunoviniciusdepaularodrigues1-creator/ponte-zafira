import numpy as np
import json

class WorldModel:
    """
    World Model Nível 16.6 Fase 2: Representation Learning.
    Inclui Encoder (Bottleneck), Decoder (Reconstrução) e Loss Dual.
    """
    def __init__(self, state_dim=10, latent_dim=2, learning_rate=0.05, beta=0.1, gamma=0.2):
        self.state_dim = state_dim
        self.latent_dim = latent_dim
        self.lr = learning_rate
        self.beta = beta   # Fator para Reconstruction Loss
        self.gamma = gamma # Fator para Contrastive Loss (N17)
        self.margin = 0.5  # Margem de separação semântica
        
        # Encoder: Mapeia state_dim -> latent_dim
        self.encoder_weights = np.random.randn(latent_dim, state_dim) * 0.1
        
        # Decoder: Mapeia latent_dim -> state_dim (Reconstrução)
        self.decoder_weights = np.random.randn(state_dim, latent_dim) * 0.1
        
        # Transição no Espaço Latente: P(z' | z, a)
        self.transition_matrix = {
            "A1": np.eye(latent_dim),
            "A2": np.eye(latent_dim),
            "A3": np.eye(latent_dim)
        }
        
        # Recompensa baseada no Espaço Latente: R(z, a)
        self.reward_model = {
            "A1": np.zeros(latent_dim),
            "A2": np.zeros(latent_dim),
            "A3": np.zeros(latent_dim)
        }
        
        self.prediction_errors = []
        self.reconstruction_errors = []
        self.contrastive_losses = []
        self.memory_buffer = [] # Para amostragem de contraste (N17)

    def encode(self, state):
        """Comprime o estado para o espaço latente (Bottleneck)."""
        latent = np.dot(self.encoder_weights, state)
        # Ativação Tanh para manter no intervalo [-1, 1]
        return np.tanh(latent)

    def decode(self, latent):
        """Reconstrói o estado original a partir do espaço latente."""
        reconstructed = np.dot(self.decoder_weights, latent)
        # Normalização para manter a escala do state_vector original
        norm = np.linalg.norm(reconstructed) + 1e-9
        return reconstructed / norm

    def predict(self, state, action):
        """Prediz o próximo estado (via latente) e recompensa."""
        latent = self.encode(state)
        
        if action not in self.transition_matrix:
            return state, 0.5
        
        # Predição no espaço latente
        next_latent = np.dot(self.transition_matrix[action], latent)
        next_latent = np.tanh(next_latent)
        
        # Reconstrói o próximo estado predito
        next_state_pred = self.decode(next_latent)
        
        # Predição de recompensa baseada no latente
        expected_reward = np.dot(self.reward_model[action], latent)
        expected_reward = 1.0 / (1.0 + np.exp(-expected_reward)) # Sigmoid
        
        return next_state_pred, expected_reward

    def update(self, state, action, next_state, actual_reward):
        """Treina o modelo com Loss Tripla: Reward + Recon + Contrastive (N17)."""
        latent = self.encode(state)
        next_latent_actual = self.encode(next_state)
        
        # Salva na memória para amostragem futura
        self.memory_buffer.append((state, latent))
        if len(self.memory_buffer) > 100: self.memory_buffer.pop(0)
        
        # 1. Predição e Erros Base
        pred_state, pred_reward = self.predict(state, action)
        reward_error = abs(actual_reward - pred_reward)
        self.prediction_errors.append(reward_error)
        
        reconstructed_state = self.decode(latent)
        recon_error = np.linalg.norm(state - reconstructed_state)
        self.reconstruction_errors.append(recon_error)
        
        # 2. Contrastive Loss (N17)
        contrast_loss = 0
        if len(self.memory_buffer) > 5:
            # Amostragem simples: Positivo (vizinho no tempo) vs Negativo (aleatório)
            pos_idx = max(0, len(self.memory_buffer) - 2)
            neg_idx = np.random.randint(0, len(self.memory_buffer))
            
            z_pos = self.memory_buffer[pos_idx][1]
            z_neg = self.memory_buffer[neg_idx][1]
            
            d_pos = np.linalg.norm(latent - z_pos)
            d_neg = np.linalg.norm(latent - z_neg)
            
            # Hinge Loss: d_pos deve ser pequeno, d_neg deve ser maior que a margem
            contrast_loss = max(0, self.margin + d_pos - d_neg)
            self.contrastive_losses.append(contrast_loss)
            
            # Ajuste do Encoder via Contraste (Empurra z para perto de z_pos e longe de z_neg)
            contrast_grad = self.lr * self.gamma * ( (z_pos - latent) - (z_neg - latent) )
            self.encoder_weights += np.outer(contrast_grad, state)

        # 3. Atualização de Pesos (Reward + Recon)
        self.reward_model[action] += self.lr * (actual_reward - pred_reward) * latent
        
        latent_diff = (next_latent_actual - self.encode(pred_state)).reshape(-1, 1)
        latent_input = latent.reshape(1, -1)
        self.transition_matrix[action] += self.lr * np.dot(latent_diff, latent_input)
        
        state_diff = (state - reconstructed_state).reshape(-1, 1)
        self.decoder_weights += self.lr * self.beta * np.dot(state_diff, latent_input)
        
        encoder_grad = self.lr * (reward_error * 0.5 + recon_error * self.beta)
        self.encoder_weights += encoder_grad * np.outer(latent, state)
        
        return reward_error

    def get_avg_error(self):
        if not self.prediction_errors: return 1.0
        return np.mean(self.prediction_errors[-50:])

    def get_avg_recon_error(self):
        if not self.reconstruction_errors: return 1.0
        return np.mean(self.reconstruction_errors[-50:])

    def get_avg_contrast_loss(self):
        if not self.contrastive_losses: return 0.0
        return np.mean(self.contrastive_losses[-50:])

    def simulate_sequence(self, state, actions_list):
        """Simula uma sequência de ações e retorna a recompensa acumulada."""
        total_reward = 0
        current_state = state
        
        for action in actions_list:
            next_state, reward = self.predict(current_state, action)
            total_reward += reward
            current_state = next_state
            
        return total_reward
