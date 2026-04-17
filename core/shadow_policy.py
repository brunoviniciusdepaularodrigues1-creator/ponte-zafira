import numpy as np
import copy

class ShadowPolicy:
    """
    Shadow Mode Nível 11: Testa novas estratégias em paralelo sem afetar a produção.
    Só propõe mudança se a performance for superior à política atual.
    """
    def __init__(self, current_policy):
        self.original_policy = current_policy
        self.shadow_stats = copy.deepcopy(current_policy.stats)
        self.mutation_budget = 0.1 # Max 10% de alteração nos parâmetros
        self.shadow_performance = []
        self.original_performance = []
        
        # Parâmetros mutados para teste
        self.shadow_entropy_threshold = current_policy.entropy_threshold * (1 + np.random.uniform(-self.mutation_budget, self.mutation_budget))
        self.shadow_exploration_boost = current_policy.exploration_boost * (1 + np.random.uniform(-self.mutation_budget, self.mutation_budget))

    def update_both(self, action, reward, is_shadow_choice=False):
        """Atualiza estatísticas para comparação."""
        if is_shadow_choice:
            self.shadow_performance.append(reward)
        else:
            self.original_performance.append(reward)

    def evaluate_promotion(self):
        """Verifica se a política shadow deve ser promovida."""
        if len(self.shadow_performance) < 10:
            return False
        
        shadow_avg = np.mean(self.shadow_performance)
        original_avg = np.mean(self.original_performance) if self.original_performance else 0.5
        
        # Só promove se o ganho for real (> 5% de melhoria)
        return shadow_avg > (original_avg * 1.05)

    def get_mutated_params(self):
        return {
            "entropy_threshold": self.shadow_entropy_threshold,
            "exploration_boost": self.shadow_exploration_boost
        }
