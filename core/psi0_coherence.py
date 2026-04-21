import json
import os

class CoherenceLayer:
    def __init__(self, path=None):
        self.path = path or os.path.join(os.path.dirname(__file__), "coherence_policy.json")
        self.global_policy = self._load()

    def _load(self):
        if os.path.exists(self.path):
            with open(self.path, "r") as f:
                return json.load(f)
        return {"A1": 0.33, "A2": 0.33, "A3": 0.34}

    def save(self):
        with open(self.path, "w") as f:
            json.dump(self.global_policy, f, indent=2)

    def update(self, action, reward, lr=0.01):
        self.global_policy[action] += lr * (reward - self.global_policy[action])
        self._normalize()
        self.save()

    def _normalize(self):
        total = sum(self.global_policy.values())
        for k in self.global_policy:
            self.global_policy[k] /= total

    def apply_bias(self, actor_probs):
        """
        Ajusta levemente a política do Actor sem destruir aprendizado.
        """
        blended = {}
        alpha = 0.15  # peso da coerência global

        for k in actor_probs:
            blended[k] = (
                (1 - alpha) * actor_probs[k] +
                alpha * self.global_policy.get(k, 0.33)
            )

        # renormaliza
        s = sum(blended.values())
        for k in blended:
            blended[k] /= s

        return blended

    def get_dominant(self):
        return max(self.global_policy, key=self.global_policy.get)

    def apply_contextual_bias(self, actor_probs, strategy_bias):
        """
        Combina actor_probs com bias de estratégia contextual e política global.
        Três níveis: actor (local) + strategy (contextual) + global (coherence)
        """
        blended = {}
        alpha_global = 0.10   # peso da coerência global
        alpha_strategy = 0.20  # peso do routing contextual
        alpha_actor = 0.70     # peso do actor
        
        for k in actor_probs:
            blended[k] = (
                alpha_actor * actor_probs.get(k, 0.33) +
                alpha_strategy * strategy_bias.get(k, 0.33) +
                alpha_global * self.global_policy.get(k, 0.33)
            )
        
        # renormaliza
        s = sum(blended.values())
        for k in blended:
            blended[k] /= s
        
        return blended
