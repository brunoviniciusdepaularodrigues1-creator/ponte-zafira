import math
import random
import json
import os

class PolicyActor:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "actor_weights.json")
        self.weights = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {
            "C": {"A1": 0.3, "A2": 0.3, "A3": 0.4},
            "F": {"A1": 0.3, "A2": 0.4, "A3": 0.3},
            "A": {"A1": 0.4, "A2": 0.3, "A3": 0.3}
        }

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.weights, f, indent=2)

    def softmax(self, stage):
        w = self.weights.get(stage, {"A1": 0.33, "A2": 0.33, "A3": 0.34})
        exp_vals = {k: math.exp(v) for k, v in w.items()}
        total = sum(exp_vals.values())
        probs = {k: v / total for k, v in exp_vals.items()}
        return probs

    def select(self, stage):
        probs = self.softmax(stage)
        chosen = random.choices(
            list(probs.keys()),
            weights=list(probs.values())
        )[0]
        return chosen, probs

    def update(self, stage, action, advantage, lr=0.05):
        if stage not in self.weights:
            self.weights[stage] = {"A1": 0.33, "A2": 0.33, "A3": 0.34}
        if action not in self.weights[stage]:
            self.weights[stage][action] = 0.33
        self.weights[stage][action] += lr * advantage
        self.save()
