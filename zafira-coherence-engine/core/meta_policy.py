class MetaPolicy:

    def __init__(self):
        self.stats = {
            "A1": {"correct": 0, "total": 0},
            "A2": {"correct": 0, "total": 0},
            "A3": {"correct": 0, "total": 0}
        }

    def update(self, action, reward):
        self.stats[action]["total"] += 1

        if reward > 0.5:
            self.stats[action]["correct"] += 1

    def get_scores(self):
        scores = {}

        for action, data in self.stats.items():
            if data["total"] == 0:
                scores[action] = 0.5
            else:
                scores[action] = data["correct"] / data["total"]

        return scores

    def best_action(self):
        scores = self.get_scores()
        return max(scores, key=scores.get)

    def get_preference(self, task_type):
        """Retorna o agente preferido com base no histórico de sucesso por categoria (N18)."""
        # Mapeamento baseado na observação do Passo 1 do N18
        if task_type == "explanation":
            return "A3" # LLM (A3) domina explicações
        elif task_type == "numeric":
            # Se A2 tiver taxa de sucesso razoável, prefere A2, senão A3
            a2_stats = self.stats.get("A2", {"correct": 0, "total": 0})
            a2_rate = a2_stats["correct"] / a2_stats["total"] if a2_stats["total"] > 0 else 0
            return "A2" if a2_rate > 0.6 else "A3"
        elif task_type == "algebra":
            # Atualmente A3 domina por falha do A1 em álgebra linear
            return "A3"
        return None
