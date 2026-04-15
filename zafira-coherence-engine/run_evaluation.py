import sys
import os
from collections import defaultdict

# Adiciona o diretório atual ao sys.path para imports locais
sys.path.insert(0, os.path.dirname(__file__))
# Adiciona o diretório pai para imports do core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_benchmark import BENCHMARK
from core.psi0_evaluation_harness import EvaluationHarness
from core.psi0_evaluation_harness import compute_system_performance
from core.psi0_actor import PolicyActor
from core.psi0_value_function import ValueFunction
from core.psi0_coherence import CoherenceLayer
from core.action_space import ACTIONS

# Cria os objetos UMA vez para persistência do aprendizado durante a sessão de teste
actor = PolicyActor()
value_fn = ValueFunction()
coherence = CoherenceLayer()

harness = EvaluationHarness(BENCHMARK)

print("\n=== TESTE SEM COHERENCE (Generalização Real) ===")
res_a = harness.run(actor, value_fn, coherence, mode="without_coherence")
score_a = compute_system_performance(res_a)

for r in res_a:
    print(f"  Task: {r['task']} | Ação: {r['action']} → {r['executor']} | Score: {r['score']} | Value: {r['value']:.4f} | Advantage: {r['advantage']:.4f}")

print("SYSTEM SCORE A:", score_a)


print("\n=== TESTE COM COHERENCE (Generalização Real) ===")
res_b = harness.run(actor, value_fn, coherence, mode="with_coherence")
score_b = compute_system_performance(res_b)

for r in res_b:
    print(f"  Task: {r['task']} | Ação: {r['action']} → {r['executor']} | Score: {r['score']} | Value: {r['value']:.4f} | Advantage: {r['advantage']:.4f}")

print("SYSTEM SCORE B:", score_b)


print("\n=== DIFERENÇA ===")
print("Δ:", score_b - score_a)

# Specialization signal
success_by_action = defaultdict(lambda: {"wins": 0, "total": 0})

for r in res_a + res_b:
    success_by_action[r["action"]]["total"] += 1
    if r["score"] == 1.0:
        success_by_action[r["action"]]["wins"] += 1

print("\n=== SPECIALIZATION SIGNAL ===")
for action, stats in success_by_action.items():
    rate = stats["wins"] / stats["total"] if stats["total"] > 0 else 0
    print(f"  {action} ({ACTIONS[action]}): {stats['wins']}/{stats['total']} = {rate:.2f}")
