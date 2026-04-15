import sys
import os

# Adiciona o diretório atual ao sys.path para imports locais
sys.path.insert(0, os.path.dirname(__file__))
# Adiciona o diretório pai para imports do core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_benchmark import BENCHMARK
from core.psi0_evaluation_harness import EvaluationHarness
from core.psi0_evaluation_harness import compute_system_performance


harness = EvaluationHarness(BENCHMARK)

print("\n=== TESTE SEM COHERENCE ===")
res_a = harness.run(mode="without_coherence")
score_a = compute_system_performance(res_a)

for r in res_a:
    print(f"  Task: {r['task']} | Ação: {r['action']} → {r['executor']} | Score: {r['score']} | Value: {r['value']:.4f} | Advantage: {r['advantage']:.4f}")

print("SYSTEM SCORE A:", score_a)


print("\n=== TESTE COM COHERENCE ===")
res_b = harness.run(mode="with_coherence")
score_b = compute_system_performance(res_b)

for r in res_b:
    print(f"  Task: {r['task']} | Ação: {r['action']} → {r['executor']} | Score: {r['score']} | Value: {r['value']:.4f} | Advantage: {r['advantage']:.4f}")

print("SYSTEM SCORE B:", score_b)


print("\n=== DIFERENÇA ===")
print("Δ:", score_b - score_a)
