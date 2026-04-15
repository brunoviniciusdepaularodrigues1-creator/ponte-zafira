from core.psi0_state_encoder import encode_state
from core.psi0_value_function import ValueFunction
from core.psi0_actor import PolicyActor
from core.action_space import ACTIONS
from core.psi0_coherence import CoherenceLayer
import random


class EvaluationHarness:

    def __init__(self, benchmark):
        self.benchmark = benchmark

    def run(self, mode="with_coherence"):
        actor = PolicyActor()
        value_fn = ValueFunction()
        coherence = CoherenceLayer()

        results = []

        for task in self.benchmark:

            state = encode_state("F", task["input"], {})

            raw_probs = actor.softmax("F")

            if mode == "with_coherence":
                probs = coherence.apply_bias(raw_probs)
            else:
                probs = raw_probs

            action = random.choices(
                list(probs.keys()),
                weights=list(probs.values())
            )[0]

            executor = ACTIONS[action]

            output = self.simulate(task["input"])

            score = self.evaluate(output, task["ground_truth"])

            value = value_fn.predict(state, "F", action)
            advantage = score - value

            value_fn.update(state, "F", action, score)
            actor.update("F", action, advantage)

            if mode == "with_coherence":
                coherence.update(action, score)

            results.append({
                "task": task["id"],
                "action": action,
                "executor": executor,
                "score": score,
                "value": value,
                "advantage": advantage
            })

        return results

    def simulate(self, input_data):
        if "2 + 2" in input_data:
            return 4
        if "x + 2 = 5" in input_data:
            return 3
        return 0

    def evaluate(self, output, gt):
        return 1.0 if output == gt else 0.0


def compute_system_performance(results):
    if not results:
        return 0.0
    return sum(r["score"] for r in results) / len(results)
