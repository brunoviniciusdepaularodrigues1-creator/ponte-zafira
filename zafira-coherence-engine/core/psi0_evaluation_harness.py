from core.psi0_state_encoder import encode_state
from core.psi0_value_function import ValueFunction
from core.psi0_actor import PolicyActor
from core.action_space import ACTIONS
from core.psi0_coherence import CoherenceLayer
from core.dispatcher import execute
import random


class EvaluationHarness:

    def __init__(self, benchmark, executor_fn=None):
        self.benchmark = benchmark
        self.executor_fn = executor_fn

    def run(self, actor, value_fn, coherence, mode="with_coherence"):
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

            if self.executor_fn is not None:
                output = self.executor_fn(task["input"])
            else:
                output = execute(action, task["input"])

            score = self.evaluate(output, task["ground_truth"])

            value = value_fn.predict(state, "F", action)
            advantage = score - value

            # NÃO atualizar nada aqui — apenas medir (frozen policy)
            # value_fn.update, actor.update, coherence.update REMOVIDOS

            results.append({
                "task": task["id"],
                "action": action,
                "executor": executor,
                "score": score,
                "value": value,
                "advantage": advantage
            })

        return results

    def evaluate(self, output, gt):
        try:
            # Compara numericamente para evitar problemas de tipo (int vs float)
            return 1.0 if float(output) == float(gt) else 0.0
        except:
            return 0.0


def compute_system_performance(results):
    if not results:
        return 0.0
    return sum(r["score"] for r in results) / len(results)
