import numpy as np
import json

class WorldModel:
    """
    World Model N17.2 — Anti-Colapso com Diversidade Geométrica Real.

    Modificações N17.2:
      1. Normalização do latente (encode retorna vetor unitário)
      2. Contraste com Temperatura (cosine similarity / tau)
      3. Stop-Gradient (z_pos e z_neg são referências fixas)
      4. Variance Regularization (penaliza colapso da janela latente)
      5. Loss Final Unificada: reward + beta*recon + contrast + gamma*var_loss

    Parâmetros seguros:
      beta  = 0.5   (peso da reconstruction loss)
      gamma = 0.1   (peso da variance regularization)
      tau   = 0.1   (temperatura do contraste cosine)
    """

    def __init__(self, state_dim=10, latent_dim=2,
                 learning_rate=0.05, beta=0.5, gamma=0.1, tau=0.1):
        self.state_dim = state_dim
        self.latent_dim = latent_dim
        self.lr = learning_rate
        self.beta = beta    # Reconstruction loss weight
        self.gamma = gamma  # Variance regularization weight
        self.tau = tau      # Contrastive temperature

        # Encoder: state_dim → latent_dim
        self.encoder_weights = np.random.randn(latent_dim, state_dim) * 0.1

        # Decoder: latent_dim → state_dim
        self.decoder_weights = np.random.randn(state_dim, latent_dim) * 0.1

        # Transição no espaço latente: P(z' | z, a)
        self.transition_matrix = {
            "A1": np.eye(latent_dim),
            "A2": np.eye(latent_dim),
            "A3": np.eye(latent_dim)
        }

        # Recompensa baseada no espaço latente: R(z, a)
        self.reward_model = {
            "A1": np.zeros(latent_dim),
            "A2": np.zeros(latent_dim),
            "A3": np.zeros(latent_dim)
        }

        self.prediction_errors = []
        self.reconstruction_errors = []
        self.contrastive_losses = []
        self.variance_losses = []
        self.latent_history = []   # Janela para variance regularization
        self.memory_buffer = []    # Para amostragem de contraste

    # ──────────────────────────────────────────────────────────────
    # MODIFICAÇÃO 1: Normalização do Latente
    # ──────────────────────────────────────────────────────────────

    def encode(self, state):
        """
        Comprime o estado para o espaço latente.
        N17.2: Normaliza o vetor latente para a hiperesfera unitária.
        Sem normalização → vetores colapsam para a mesma região.
        """
        z = np.tanh(np.dot(self.encoder_weights, state))
        norm = np.linalg.norm(z) + 1e-8
        return z / norm  # Vetor unitário — diversidade geométrica garantida

    def decode(self, latent):
        """Reconstrói o estado original a partir do espaço latente."""
        reconstructed = np.dot(self.decoder_weights, latent)
        norm = np.linalg.norm(reconstructed) + 1e-9
        return reconstructed / norm

    # ──────────────────────────────────────────────────────────────
    # MODIFICAÇÃO 2 + 3: Contraste com Temperatura + Stop-Gradient
    # ──────────────────────────────────────────────────────────────

    @staticmethod
    def _cosine_sim(a, b):
        """Similaridade cosseno entre dois vetores normalizados."""
        return float(np.dot(a, b))

    def _contrastive_loss_temperature(self, z, z_pos_ref, z_neg_ref):
        """
        Contrastive Loss com Temperatura (N17.2).
        z_pos e z_neg são referências fixas (stop-gradient):
          → apenas z recebe atualização.
        Loss = max(0, 1 + sim_neg/tau - sim_pos/tau)
        """
        # Stop-gradient: copia sem referência ao grafo de computação
        z_pos = z_pos_ref.copy()
        z_neg = z_neg_ref.copy()

        sim_pos = self._cosine_sim(z, z_pos) / self.tau
        sim_neg = self._cosine_sim(z, z_neg) / self.tau

        loss = max(0.0, 1.0 + sim_neg - sim_pos)

        # Gradiente: empurra z para perto de z_pos e longe de z_neg
        if loss > 0:
            grad = (z_pos / self.tau) - (z_neg / self.tau)
            return loss, grad
        return loss, np.zeros_like(z)

    # ──────────────────────────────────────────────────────────────
    # MODIFICAÇÃO 4: Variance Regularization
    # ──────────────────────────────────────────────────────────────

    def _variance_loss(self):
        """
        Penaliza colapso: força variância mínima na janela de latentes.
        var_loss = 1.0 - mean_variance (quanto menor a var, maior a penalidade)
        """
        if len(self.latent_history) < 5:
            return 0.0, np.zeros(self.latent_dim)

        window = np.array(self.latent_history[-10:])  # Janela de 10
        var_per_dim = np.var(window, axis=0)
        mean_var = float(np.mean(var_per_dim))
        var_loss = max(0.0, 1.0 - mean_var)

        # Gradiente: empurra z para longe da média (aumenta dispersão)
        mean_z = np.mean(window, axis=0)
        grad = np.zeros(self.latent_dim)
        if var_loss > 0 and len(self.latent_history) > 0:
            last_z = self.latent_history[-1]
            grad = -(last_z - mean_z) * 0.1  # Suave para não desestabilizar

        return var_loss, grad

    # ──────────────────────────────────────────────────────────────
    # MODIFICAÇÃO 5: Loss Final Unificada
    # ──────────────────────────────────────────────────────────────

    def update(self, state, action, next_state, actual_reward):
        """
        Treina com Loss Final Unificada N17.2:
          total_loss = reward_error + beta*recon_loss + contrast_loss + gamma*var_loss
        """
        z = self.encode(state)
        next_z_actual = self.encode(next_state)

        # Registra na janela de variância e memória de contraste
        self.latent_history.append(z.copy())
        if len(self.latent_history) > 50:
            self.latent_history.pop(0)
        self.memory_buffer.append((state, z.copy()))
        if len(self.memory_buffer) > 100:
            self.memory_buffer.pop(0)

        # ── Reward Loss ──
        pred_state, pred_reward = self.predict(state, action)
        reward_error = abs(actual_reward - pred_reward)
        self.prediction_errors.append(reward_error)

        # ── Reconstruction Loss ──
        reconstructed = self.decode(z)
        recon_error = float(np.linalg.norm(state - reconstructed))
        self.reconstruction_errors.append(recon_error)

        # ── Contrastive Loss com Temperatura (N17.2) ──
        contrast_loss = 0.0
        contrast_grad = np.zeros(self.latent_dim)
        if len(self.memory_buffer) > 5:
            pos_idx = max(0, len(self.memory_buffer) - 2)
            neg_idx = np.random.randint(0, len(self.memory_buffer))
            z_pos_ref = self.memory_buffer[pos_idx][1]
            z_neg_ref = self.memory_buffer[neg_idx][1]

            contrast_loss, contrast_grad = self._contrastive_loss_temperature(
                z, z_pos_ref, z_neg_ref
            )
            self.contrastive_losses.append(contrast_loss)

        # ── Variance Regularization (N17.2) ──
        var_loss, var_grad = self._variance_loss()
        self.variance_losses.append(var_loss)

        # ── Loss Total ──
        total_loss = (
            reward_error
            + self.beta * recon_error
            + contrast_loss
            + self.gamma * var_loss
        )

        # ── Atualização do Encoder (apenas z recebe gradiente) ──
        encoder_grad = self.lr * (
            reward_error * 0.5
            + recon_error * self.beta
            + contrast_grad
            + self.gamma * var_grad
        )
        self.encoder_weights += np.outer(encoder_grad, state)

        # ── Atualização dos Outros Módulos ──
        self.reward_model[action] += self.lr * (actual_reward - pred_reward) * z

        latent_diff = (next_z_actual - self.encode(pred_state)).reshape(-1, 1)
        latent_input = z.reshape(1, -1)
        self.transition_matrix[action] += self.lr * np.dot(latent_diff, latent_input)

        state_diff = (state - reconstructed).reshape(-1, 1)
        self.decoder_weights += self.lr * self.beta * np.dot(state_diff, latent_input)

        return total_loss

    def predict(self, state, action):
        """Prediz o próximo estado e recompensa via espaço latente."""
        z = self.encode(state)

        if action not in self.transition_matrix:
            return state, 0.5

        next_z = np.tanh(np.dot(self.transition_matrix[action], z))
        norm = np.linalg.norm(next_z) + 1e-8
        next_z = next_z / norm

        next_state_pred = self.decode(next_z)

        expected_reward = np.dot(self.reward_model[action], z)
        expected_reward = 1.0 / (1.0 + np.exp(-expected_reward))

        return next_state_pred, float(expected_reward)

    # ──────────────────────────────────────────────────────────────
    # TELEMETRIA N17.2
    # ──────────────────────────────────────────────────────────────

    def get_avg_error(self):
        if not self.prediction_errors: return 1.0
        return float(np.mean(self.prediction_errors[-50:]))

    def get_avg_recon_error(self):
        if not self.reconstruction_errors: return 1.0
        return float(np.mean(self.reconstruction_errors[-50:]))

    def get_avg_contrast_loss(self):
        if not self.contrastive_losses: return 0.0
        return float(np.mean(self.contrastive_losses[-50:]))

    def get_avg_variance(self):
        """Variância média do espaço latente (janela de 10)."""
        if len(self.latent_history) < 2: return 0.0
        window = np.array(self.latent_history[-10:])
        return float(np.mean(np.var(window, axis=0)))

    def get_avg_norm(self):
        """Norma média dos vetores latentes (deve ser ~1.0 após normalização)."""
        if not self.latent_history: return 0.0
        norms = [float(np.linalg.norm(z)) for z in self.latent_history[-10:]]
        return float(np.mean(norms))

    def get_entropy_proxy(self):
        """
        Proxy de entropia: variância normalizada do espaço latente.
        0.0 = colapso total | >0.01 = diversidade geométrica presente.
        """
        return self.get_avg_variance()

    def get_telemetry(self):
        """Retorna telemetria completa N17.2 para logging."""
        return {
            "entropy_proxy": round(self.get_entropy_proxy(), 6),
            "latent_variance": round(self.get_avg_variance(), 6),
            "avg_norm": round(self.get_avg_norm(), 4),
            "prediction_error": round(self.get_avg_error(), 4),
            "recon_error": round(self.get_avg_recon_error(), 4),
            "contrast_loss": round(self.get_avg_contrast_loss(), 4),
            "var_loss": round(float(np.mean(self.variance_losses[-50:])) if self.variance_losses else 0.0, 4),
            "cycles": len(self.prediction_errors)
        }

    def simulate_sequence(self, state, actions_list):
        """Simula uma sequência de ações e retorna a recompensa acumulada."""
        total_reward = 0
        current_state = state
        for action in actions_list:
            next_state, reward = self.predict(current_state, action)
            total_reward += reward
            current_state = next_state
        return total_reward
