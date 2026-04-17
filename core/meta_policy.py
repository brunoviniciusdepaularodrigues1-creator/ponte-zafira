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
