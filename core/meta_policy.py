import numpy as np

class MetaPolicy:
    """
    MetaPolicy Nível 9: Sistema de controle auto-equilibrado via Entropia de Shannon.
    Implementa exploração adaptativa para evitar o colapso de estratégia.
    """
    def __init__(self, entropy_threshold=0.5, exploration_boost=0.3):
        self.stats = {
            "A1": {"correct": 0, "total": 0},
            "A2": {"correct": 0, "total": 0},
            "A3": {"correct": 0, "total": 0}
        }
        self.entropy_threshold = entropy_threshold
        self.exploration_boost = exploration_boost
        self.history = []

    def update(self, action, reward):
        self.stats[action]["total"] += 1
        if reward > 0.5:
            self.stats[action]["correct"] += 1
        self.history.append(action)

    def calculate_entropy(self):
        totals = np.array([data["total"] for data in self.stats.values()])
        if totals.sum() == 0:
            return 1.58  # Entropia máxima para 3 opções (log2(3))
        
        probs = totals / totals.sum()
        # Evitar log(0)
        probs = np.where(probs > 0, probs, 1e-10)
        entropy = -np.sum(probs * np.log2(probs))
        return entropy

    def get_scores(self):
        scores = {}
        entropy = self.calculate_entropy()
        total_runs = sum(d["total"] for d in self.stats.values())
        
        # Mecanismo de Controle N9: Se entropia < threshold, aumenta agressivamente a exploração
        is_low_entropy = entropy < self.entropy_threshold
        
        # Garantimos uma exploração mínima (epsilon-greedy adaptativo)
        epsilon = self.exploration_boost if is_low_entropy else 0.05

        for action, data in self.stats.items():
            if data["total"] == 0:
                scores[action] = 2.0  # Prioridade absoluta para novos agentes
            else:
                usage_ratio = data["total"] / total_runs
                success_rate = data["correct"] / data["total"]
                
                # Bônus de exploração inversamente proporcional ao uso (UCB-style adaptado)
                exploration_bonus = epsilon * np.sqrt(np.log(total_runs + 1) / (data["total"] + 1))
                scores[action] = success_rate + exploration_bonus

        return scores, entropy

    def best_action(self):
        scores, _ = self.get_scores()
        return max(scores, key=scores.get)

    def get_distribution(self):
        total_executions = sum(d["total"] for d in self.stats.values())
        if total_executions == 0:
            return {k: 0.0 for k in self.stats.keys()}
        return {k: (d["total"] / total_executions) for k, d in self.stats.items()}
