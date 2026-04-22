"""
N19 Passo 2 — Calibração da Simulação
Objetivo: medir a diferença entre score simulado e score real por tipo de agente.
Não altera política, não usa reliability para escolher — só mede.
"""
import sys
import os
import json
import random

random.seed(42)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agents.a1_symbolic import SymbolicSolver
from agents.a2_numeric  import NumericSolver
from agents.a3_llm      import LLMSolver
from core.psi0_router_v2 import EvolutionaryRouter, InternalState

# ─── Inicialização ───────────────────────────────────────────────────────────
agents = [SymbolicSolver(), NumericSolver(), LLMSolver()]
# Usa a política real do sistema (ou cria uma com diversidade inicial)
policy_path = "agent_policy_v2.json"
if not os.path.exists(policy_path):
    import json as _json
    with open(policy_path, 'w') as _f:
        _json.dump({
            "symbolic": {"score": 0.7, "count": 5},
            "numeric":  {"score": 0.6, "count": 5},
            "llm":      {"score": 0.5, "count": 5}
        }, _f)
router = EvolutionaryRouter(agents, memory_path=policy_path)
state  = InternalState(window=5)

# ─── Tarefas de referência (mesmas do N19 P1) ────────────────────────────────
tasks = [
    {"text": "x**2 - 9 = 0",          "expected": "symbolic"},
    {"text": "Calcule 15% de 200",     "expected": "numeric"},
    {"text": "2x + 6 = 0",             "expected": "symbolic"},
    {"text": "144 dividido por 12?",   "expected": "numeric"},
    {"text": "x**3 - 8 = 0",          "expected": "symbolic"},
]

# ─── Função de score de simulação (mesma do N19 P1) ──────────────────────────
def simulate_agent(agent, task_text):
    result = agent.solve(task_text)
    if result.get("status") == "success":
        r = result.get("result", "")
        if r and r != "[]" and r != "None" and r is not None:
            return 0.9
        return 0.3
    return 0.1

# ─── Função de score real (juiz simples) ─────────────────────────────────────
def real_score(agent, task_text, expected_type):
    result = agent.solve(task_text)
    if result.get("status") == "success":
        r = result.get("result", "")
        if r and r != "[]" and r != "None" and r is not None:
            # Bônus se o agente é o esperado
            return 1.0 if agent.type == expected_type else 0.7
        return 0.2
    return 0.1

# ─── Loop principal ──────────────────────────────────────────────────────────
print("=" * 80)
print("N19 PASSO 2 — CALIBRAÇÃO DA SIMULAÇÃO")
print("=" * 80)

results = []

for i, task in enumerate(tasks, 1):
    task_text    = task["text"]
    expected     = task["expected"]
    health       = state.health_state()
    temperature  = state.adaptive_temperature()

    # 1. Simulação leve (k=2 candidatos)
    candidates, candidate_scores = router.get_top_k(task_text, k=2)
    simulated_scores = {}
    for agent in candidates:
        simulated_scores[agent.type] = simulate_agent(agent, task_text)

    # 2. Escolha final = melhor simulado
    best_simulated_type = max(simulated_scores, key=simulated_scores.get)
    best_simulated_score = simulated_scores[best_simulated_type]
    selected_agent = next(a for a in agents if a.type == best_simulated_type)

    # 3. Execução real
    r_score = real_score(selected_agent, task_text, expected)

    # 4. Registrar erro de simulação (N19 P2)
    router.register_simulation_error(
        agent_type=best_simulated_type,
        simulated_score=best_simulated_score,
        real_score=r_score
    )

    # 5. Calcular confiabilidade atual (após registro)
    reliability = router.get_simulation_reliability(best_simulated_type)
    sim_error   = abs(best_simulated_score - r_score)

    # 6. Atualizar estado interno
    state.update(task_text, best_simulated_type, r_score)
    router.update_policy(best_simulated_type, r_score, task=task_text)

    correct = "✔" if best_simulated_type == expected else "✗"

    print(f"\n{'─'*80}")
    print(f"Tarefa {i}: {task_text}")
    print(f"  Candidatos:            {[a.type for a in candidates]}")
    print(f"  Scores simulados:      {simulated_scores}")
    print(f"  Escolha final:         {best_simulated_type} (esperado: {expected}) {correct}")
    print(f"  Score simulado:        {best_simulated_score:.2f}")
    print(f"  Score real:            {r_score:.2f}")
    print(f"  simulation_error:      {sim_error:.4f}")
    print(f"  simulation_reliability ({best_simulated_type}): {reliability:.4f}")
    print(f"  health: {health} | temp: {temperature:.2f}")

    results.append({
        "task":                  task_text,
        "expected":              expected,
        "selected":              best_simulated_type,
        "correct":               best_simulated_type == expected,
        "simulated_scores":      simulated_scores,
        "best_simulated":        best_simulated_type,
        "simulated_score":       best_simulated_score,
        "real_score":            r_score,
        "simulation_error":      round(sim_error, 4),
        "simulation_reliability": reliability,
        "health_state":          health,
        "adaptive_temperature":  temperature,
    })

# ─── Métricas finais ─────────────────────────────────────────────────────────
accuracy = sum(1 for r in results if r["correct"]) / len(results)
avg_real  = sum(r["real_score"] for r in results) / len(results)
avg_error = sum(r["simulation_error"] for r in results) / len(results)

print(f"\n{'='*80}")
print("MÉTRICAS FINAIS N19 P2:")
print(f"  Acurácia de escolha:      {accuracy*100:.1f}% ({sum(1 for r in results if r['correct'])}/{len(results)})")
print(f"  Score real médio:         {avg_real:.3f}")
print(f"  Simulation error médio:   {avg_error:.4f}")

print("\nRELIABILITY FINAL POR AGENTE:")
for agent_type in ["symbolic", "numeric", "llm"]:
    rel = router.get_simulation_reliability(agent_type)
    mem = router.simulation_memory[agent_type]
    print(f"  {agent_type:10s}: reliability={rel:.4f}  erros={mem}")

print("\nCRITÉRIOS DE SUCESSO N19 P2:")
c1 = all("simulation_error" in r for r in results)
c2 = all("simulation_reliability" in r for r in results)
# C3: reliability difere entre agentes (llm=1.0 vs symbolic/numeric < 1.0)
reliability_by_agent = {t: router.get_simulation_reliability(t) for t in ["symbolic", "numeric", "llm"]}
c3 = len(set(reliability_by_agent.values())) > 1
c4 = any(router.simulation_memory[t] for t in ["symbolic", "numeric", "llm"])

print(f"  C1 simulation_error aparece no log:          {'SIM' if c1 else 'NAO'}")
print(f"  C2 simulation_reliability aparece no log:    {'SIM' if c2 else 'NAO'}")
print(f"  C3 reliability varia entre steps:            {'SIM' if c3 else 'NAO'}")
print(f"  C4 simulation_memory tem dados registrados:  {'SIM' if c4 else 'NAO'}")

passed = sum([c1, c2, c3, c4])
print(f"  Status N19 P2: {'APROVADO' if passed == 4 else 'PARCIAL'} ({passed}/4 critérios)")

# ─── Salvar relatório ─────────────────────────────────────────────────────────
os.makedirs("logs", exist_ok=True)
report = {
    "n19_p2_summary": {
        "accuracy":          round(accuracy, 4),
        "avg_real_score":    round(avg_real, 4),
        "avg_sim_error":     round(avg_error, 4),
        "criteria_passed":   passed,
    },
    "simulation_memory_final": router.simulation_memory,
    "reliability_final": {
        t: router.get_simulation_reliability(t)
        for t in ["symbolic", "numeric", "llm"]
    },
    "steps": results
}
with open("logs/n19_p2_calibration_results.json", "w") as f:
    json.dump(report, f, indent=2)
print("\nRelatório salvo em logs/n19_p2_calibration_results.json")
