from core.psi0_state_encoder import encode_state
from core.psi0_value_function import ValueFunction
from core.psi0_actor import PolicyActor
from core.action_space import ACTIONS
from core.psi0_coherence import CoherenceLayer
from core.dispatcher import execute
from core.psi0_router import classify_task, get_strategy_bias
from core.psi0_semantic_reward import semantic_evaluate
import random


class EvaluationHarness:

    def __init__(self, benchmark, executor_fn=None):
        self.benchmark = benchmark
        self.executor_fn = executor_fn

    def run(self, actor, value_fn, coherence, mode="with_coherence"):
        results = []

        for task in self.benchmark:

            state = encode_state("F", task["input"], {})
            
            # 🔥 Nível 7: Routing Contextual
            task_type = classify_task(task["input"])
            strategy_bias = get_strategy_bias(task_type)

            raw_probs = actor.softmax("F")

            if mode == "with_coherence":
                # 🔥 Nível 7: Coherence Dinâmica
                probs = coherence.apply_contextual_bias(raw_probs, strategy_bias)
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

            # 🔥 Nível 7: Semantic Reward
            score = semantic_evaluate(output, task["ground_truth"], task.get("alt_truth"))

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
                "advantage": advantage,
                "task_type": task_type
            })

        return results


def compute_system_performance(results):
    if not results:
        return 0.0
    return sum(r["score"] for r in results) / len(results)
