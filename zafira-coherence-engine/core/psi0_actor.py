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
            "C": {"v1": 0.3, "v2": 0.3, "llm": 0.4},
            "F": {"v1": 0.3, "v2": 0.4, "llm": 0.3},
            "A": {"v1": 0.4, "v2": 0.3, "llm": 0.3}
        }

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.weights, f, indent=2)

    def softmax(self, stage):
        w = self.weights.get(stage, {"v1": 0.33, "v2": 0.33, "llm": 0.34})
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

    def update(self, stage, executor, advantage, lr=0.05):
        if stage not in self.weights:
            self.weights[stage] = {"v1": 0.33, "v2": 0.33, "llm": 0.34}
        self.weights[stage][executor] += lr * advantage
        self.save()
