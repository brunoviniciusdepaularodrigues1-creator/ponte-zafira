from core.psi0_state_encoder import encode_state
from core.psi0_value_function import ValueFunction
from core.psi0_actor import PolicyActor
from core.action_space import ACTIONS
from core.psi0_coherence import CoherenceLayer
import random

class EvaluationHarness:

    def __init__(self, benchmark):
        self.benchmark = benchmark

    def run_policy(self, actor, value_fn, coherence):
        results = []

        for task in self.benchmark:

            state_vector = encode_state("F", task["input"], {})

            raw_probs = actor.softmax("F")
            blended = coherence.apply_bias(raw_probs)

            action = random.choices(
                list(blended.keys()),
                weights=list(blended.values())
            )[0]

            executor = ACTIONS[action]

            # SIMULA EXECUÇÃO (substituir depois por real engine)
            output = self.simulate(task["input"], executor)

            score = self.evaluate(output, task["ground_truth"])

            value = value_fn.predict(state_vector, "F", action)
            advantage = score - value

            value_fn.update(state_vector, "F", action, score)
            actor.update("F", action, advantage)

            results.append({
                "task": task["id"],
                "action": action,
                "executor": executor,
                "score": score,
                "value": value,
                "advantage": advantage
            })

        return results

    def simulate(self, input_data, executor):
        # aqui você conecta depois ao seu executor real
        try:
            # Simplificação para o benchmark proposto
            if "2 + 2" in input_data:
                return 4
            if "x + 2 = 5" in input_data:
                return 3
            return 0
        except:
            return 0

    def evaluate(self, output, ground_truth):
        return 1.0 if output == ground_truth else 0.0
