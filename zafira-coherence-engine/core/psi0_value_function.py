import json
import os
import math

class ValueFunction:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "value_memory.json")
        self.memory = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return []

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.memory, f, indent=2)

    # distância vetorial simples
    def _distance(self, a, b):
        return math.sqrt(sum((x - y) ** 2 for x, y in zip(a, b)))

    def predict(self, state_vector, stage, executor):
        if not self.memory:
            return 0.5

        best_score = 0.5

        for item in self.memory:
            dist = self._distance(state_vector, item["state_vector"])
            similarity = math.exp(-dist)  # kernel exponencial

            if item["stage"] == stage and item["executor"] == executor:
                best_score = max(best_score, item["reward"] * similarity)

        return best_score

    def update(self, state_vector, stage, executor, reward):
        self.memory.append({
            "state_vector": state_vector,
            "stage": stage,
            "executor": executor,
            "reward": reward
        })
        self.save()
