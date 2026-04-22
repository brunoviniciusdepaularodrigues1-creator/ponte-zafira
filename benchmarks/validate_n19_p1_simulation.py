"""
N19 Passo 1 — Validação: Simulação Leve de Decisão
====================================================
O sistema testa 2 candidatos virtualmente antes de escolher o real.

Pipeline N19:
  1. get_top_k(task, k=2)      → candidatos mais promissores
  2. agent.solve(task)         → simulação leve (sem atualizar estado)
  3. score_simulation(result)  → estima reward sem chamar juiz pesado
  4. best = max(simulated)     → escolha baseada em antecipação
  5. Execução real do melhor   → apenas agora o estado é atualizado

Critérios de sucesso:
  ✔ candidatos testados aparecem no log
  ✔ simulated_scores variam entre candidatos
  ✔ escolha final é o melhor simulado
  ✔ estado real só é atualizado após a escolha
"""

import sys
import os
import json
import random
import numpy as np
import re
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.psi0_router_v2 import EvolutionaryRouter, InternalState
from agents.a1_symbolic import SymbolicSolver
from agents.a2_numeric import NumericSolver


def score_simulation(result: dict, task: str) -> float:
    """
    Avaliador leve para simulação — sem LLM, sem juiz pesado.
    Estima a qualidade da resposta baseado em heurísticas simples:
      - status == "success" → base 0.6
      - resultado não vazio → +0.2
      - resultado numérico ou simbólico coerente → +0.2
    Não atualiza estado. Usado apenas para comparação entre candidatos.
    """
    if result.get("status") != "success":
        return 0.1

    result_str = str(result.get("result", "")).strip()
    if not result_str or result_str in ("None", "[]", "error"):
        return 0.2

    score = 0.6

    # Bônus por resultado numérico concreto
    if re.search(r'\d', result_str):
        score += 0.2

    # Bônus por resultado simbólico coerente (lista de soluções, expressão)
    if any(c in result_str for c in ["[", "=", "x", "sqrt", "."]):
        score += 0.1

    return min(1.0, score)


# Tarefas mistas para o teste
TASKS = [
    ("x**2 - 9 = 0",              "symbolic"),   # álgebra — A1 deve ganhar
    ("Calcule 15% de 200",        "numeric"),    # numérico — A2 deve ganhar
    ("2x + 6 = 0",                "symbolic"),   # álgebra simples
    ("Qual e 144 dividido por 12?","numeric"),   # divisão explícita
    ("x**3 - 8 = 0",              "symbolic"),   # cúbica — teste de simulação
]


def run_test():
    random.seed(42)
    np.random.seed(42)

    tmp_policy = "/tmp/test_n19_p1_policy.json"
    if os.path.exists(tmp_policy):
        os.remove(tmp_policy)

    # Agentes reais
    a1 = SymbolicSolver()
    a2 = NumericSolver()

    router = EvolutionaryRouter([a1, a2], memory_path=tmp_policy)
    state  = InternalState(window=5)

    print("=" * 100)
    print("N19 PASSO 1 — SIMULACAO LEVE DE DECISAO (ANTECIPACAO)")
    print("=" * 100)

    results = []
    correct_choices = 0

    for i, (task, expected_type) in enumerate(TASKS, 1):
        avg_reward    = state.recent_average_reward()
        adaptive_temp = state.adaptive_temperature()
        health        = state.health_state()

        # ── FASE 1: Simulação leve ──────────────────────────────────────────
        candidates, candidate_scores = router.get_top_k(task, k=2)

        simulated_scores = {}
        sim_details = {}
        for candidate in candidates:
            sim_result = candidate.solve(task)
            sim_score  = score_simulation(sim_result, task)
            simulated_scores[candidate.type] = sim_score
            sim_details[candidate.type] = {
                "status": sim_result.get("status"),
                "result": str(sim_result.get("result", ""))[:50],
                "sim_score": sim_score
            }

        # ── FASE 2: Escolha baseada na simulação ────────────────────────────
        best_type = max(simulated_scores, key=simulated_scores.get)
        best_agent = next(a for a in candidates if a.type == best_type)

        # ── FASE 3: Execução real (agora sim atualiza estado) ───────────────
        real_result = best_agent.solve(task)
        real_score  = score_simulation(real_result, task)

        # Atualiza estado e política com o resultado real
        state.update(task, best_agent.type, real_score)
        router.update_policy(best_agent.type, real_score, task=task)

        # Verifica se escolheu o agente esperado
        chose_correct = best_type == expected_type
        if chose_correct:
            correct_choices += 1

        print(f"\n{'─'*100}")
        print(f"Tarefa {i}: {task}")
        print(f"  Candidatos testados: {[c.type for c in candidates]}")
        print(f"  Scores de simulacao: {simulated_scores}")
        print(f"  Detalhes:")
        for agent_type, detail in sim_details.items():
            print(f"    [{agent_type}] status={detail['status']} result='{detail['result']}' sim_score={detail['sim_score']:.2f}")
        print(f"  >> Escolha final: {best_type} (esperado: {expected_type}) {'✔' if chose_correct else '✗'}")
        print(f"  >> Real score: {real_score:.2f} | Health: {health} | Temp: {adaptive_temp:.2f}")

        results.append({
            "step": i,
            "task": task,
            "expected": expected_type,
            "candidates": [c.type for c in candidates],
            "simulated_scores": simulated_scores,
            "chosen": best_type,
            "correct": chose_correct,
            "real_score": real_score,
            "health": health
        })

    # ─── Métricas finais ─────────────────────────────────────────────────────
    print(f"\n{'='*100}")
    print(f"METRICAS FINAIS N19 P1:")
    accuracy = correct_choices / len(TASKS)
    avg_real_score = sum(r["real_score"] for r in results) / len(results)
    print(f"  Acuracia de escolha: {accuracy*100:.1f}% ({correct_choices}/{len(TASKS)})")
    print(f"  Score real medio:    {avg_real_score:.3f}")

    # Critérios
    c1 = all(len(r["candidates"]) == 2 for r in results)
    c2 = any(
        len(set(r["simulated_scores"].values())) > 1
        for r in results
    )
    c3 = all(r["chosen"] == max(r["simulated_scores"], key=r["simulated_scores"].get) for r in results)
    c4 = accuracy >= 0.6

    print(f"\nCRITERIOS DE SUCESSO N19 P1:")
    print(f"  C1 candidatos testados (k=2) em todos os steps: {'SIM' if c1 else 'NAO'}")
    print(f"  C2 simulated_scores variam entre candidatos:    {'SIM' if c2 else 'NAO'}")
    print(f"  C3 escolha final = melhor simulado:             {'SIM' if c3 else 'NAO'}")
    print(f"  C4 acuracia >= 60%:                             {'SIM' if c4 else 'NAO'}")

    passed = sum([c1, c2, c3, c4])
    status = "APROVADO" if passed >= 3 else "PARCIAL" if passed >= 2 else "REPROVADO"
    print(f"\n  Status N19 P1: {status} ({passed}/4 criterios)")

    # Salva relatório
    report = {
        "level": "N19_P1",
        "status": status,
        "criteria_passed": passed,
        "accuracy": accuracy,
        "avg_real_score": avg_real_score,
        "results": results
    }
    os.makedirs("logs", exist_ok=True)
    with open("logs/n19_p1_simulation_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)
    print("\nRelatorio salvo em logs/n19_p1_simulation_results.json")
    return report


if __name__ == "__main__":
    run_test()
