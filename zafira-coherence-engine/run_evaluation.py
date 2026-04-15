import sys
import os

# Adiciona o diretório atual ao sys.path para imports locais
sys.path.insert(0, os.path.dirname(__file__))
# Adiciona o diretório pai para imports do core
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_benchmark import BENCHMARK
from core.psi0_evaluator import EvaluationHarness
from core.psi0_metrics import compute_system_performance
from core.psi0_actor import PolicyActor
from core.psi0_value_function import ValueFunction
from core.psi0_coherence import CoherenceLayer

print("=" * 50)
print("ZAFIRA — NÍVEL 6: EVALUATION HARNESS")
print("=" * 50)

actor = PolicyActor()
value_fn = ValueFunction()
coherence = CoherenceLayer()

harness = EvaluationHarness(BENCHMARK)

# Roda múltiplas épocas de avaliação
for epoch in range(3):
    print(f"\n--- Época {epoch + 1} ---")
    results = harness.run_policy(actor, value_fn, coherence)
    
    for r in results:
        print(f"  Task: {r['task']} | Ação: {r['action']} → {r['executor']} | Score: {r['score']} | Value: {r['value']:.4f} | Advantage: {r['advantage']:.4f}")
    
    score = compute_system_performance(results)
    print(f"  SYSTEM SCORE: {score:.2f}")

print("\n" + "=" * 50)
print("Avaliação concluída.")
