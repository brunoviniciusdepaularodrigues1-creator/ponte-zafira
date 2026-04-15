import json
import os

EXECUTOR_EMBEDDINGS = {
    "v1":  [1.0, 0.0, 0.0],
    "v2":  [0.0, 1.0, 0.0],
    "llm": [0.0, 0.0, 1.0]
}

class ValueFunction:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "value_memory.json")
        self.W = self._load_weights()

    def _load_weights(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {
            "weights": [0.1] * 8  # 5 state + 3 executor
        }

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.W, f, indent=2)

    def _build_input(self, state_vector, executor):
        return state_vector + EXECUTOR_EMBEDDINGS[executor]

    def predict(self, state_vector, stage, executor):
        x = self._build_input(state_vector, executor)
        W = self.W["weights"]
        return sum(w * xi for w, xi in zip(W, x))

    def update(self, state_vector, stage, executor, reward, lr=0.05):
        x = self._build_input(state_vector, executor)
        W = self.W["weights"]

        prediction = self.predict(state_vector, stage, executor)
        error = reward - prediction

        new_W = []
        for w, xi in zip(W, x):
            new_W.append(w + lr * error * xi)

        self.W["weights"] = new_W
        self.save()
        return prediction, new_W
