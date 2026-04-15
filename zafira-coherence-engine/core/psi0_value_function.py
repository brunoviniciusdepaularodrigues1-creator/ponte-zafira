import json
import os

class ValueFunction:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "value_memory.json")
        self.memory = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.memory, f, indent=2)

    def _key(self, stage, executor):
        return f"{stage}:{executor}"

    def predict(self, stage, executor):
        key = self._key(stage, executor)
        return self.memory.get(key, 0.5)  # valor neutro inicial

    def update(self, stage, executor, reward, lr=0.1):
        key = self._key(stage, executor)
        old = self.memory.get(key, 0.5)
        new = old + lr * (reward - old)
        self.memory[key] = round(new, 4)
        self.save()
        return old, new
