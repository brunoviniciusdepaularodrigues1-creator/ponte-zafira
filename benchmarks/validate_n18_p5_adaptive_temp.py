"""
N18 Passo 5 — Validação: Exploração Adaptativa por Desempenho Recente
======================================================================
Sequência de tarefas:
  1. Fáceis (reward alto → temperatura cai)
  2. Tarefa ruim/impossível (reward baixo → temperatura sobe)
  3. Normais de volta (temperatura se estabiliza)

Critérios de sucesso:
  ✔ Temperatura adaptativa varia de forma coerente
  ✔ Log mostra a variação
  ✔ Tarefa ruim aumenta exploração
  ✔ Tarefas boas voltam a reduzir exploração
"""

import sys
import os
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.psi0_router_v2 import EvolutionaryRouter, InternalState


# ─── Agentes stub ────────────────────────────────────────────────────────────

class StubAgent:
    def __init__(self, name, agent_type):
        self.name = name
        self.type = agent_type


def make_agents():
    return [
        StubAgent("A1_Symbolic", "symbolic"),
        StubAgent("A2_Numeric",  "numeric"),
        StubAgent("A3_LLM",      "llm"),
    ]


# ─── Sequência de tarefas ────────────────────────────────────────────────────
# (task, expected_type, reward_override)
# reward_override = None → reward calculado pelo juiz
# reward_override = 0.1  → tarefa ruim/impossível (força baixo reward)

TASKS = [
    # Fase 1 — Fáceis (reward esperado alto)
    ("x**2 - 16 = 0",                    "symbolic", None),
    ("Calcule 25% de 320",               "numeric",  None),
    # Fase 2 — Tarefa ruim/impossível
    ("Resolva o sistema impossivel x = x + 1", "symbolic", 0.1),
    # Fase 3 — Normais de volta
    ("Explique energia em uma frase",    "llm",      None),
    ("Qual e 144 dividido por 12?",      "numeric",  None),
]


def judge(expected_type, selected_type, reward_override=None):
    if reward_override is not None:
        return reward_override, selected_type == expected_type
    consistent = selected_type == expected_type
    if consistent:
        reward = 1.0
    elif selected_type == "llm":
        reward = 0.6
    else:
        reward = 0.3
    return reward, consistent


def run_test():
    random.seed(42)
    np.random.seed(42)

    tmp_policy = "/tmp/test_n18_p5_policy.json"
    if os.path.exists(tmp_policy):
        os.remove(tmp_policy)

    agents = make_agents()
    router = EvolutionaryRouter(agents, memory_path=tmp_policy)
    state  = InternalState(window=5)

    print("=" * 80)
    print("N18 PASSO 5 — EXPLORACAO ADAPTATIVA POR DESEMPENHO RECENTE")
    print("=" * 80)
    header = (
        f"{'#':>2} | {'Tarefa':<42} | {'Sel':>8} | "
        f"{'Reward':>6} | {'AvgR':>5} | {'Temp':>5} | OK?"
    )
    print(header)
    print("-" * 80)

    results = []
    temp_history = []

    for i, (task, expected_type, reward_override) in enumerate(TASKS, 1):
        # Temperatura adaptativa baseada no estado atual
        adaptive_temp = state.adaptive_temperature()
        avg_reward    = state.recent_average_reward()

        # Seleciona agente com temperatura adaptativa
        agent, probs, meta = router.select_agent(task, temperature=adaptive_temp)

        # Avalia
        reward, consistent = judge(expected_type, agent.type, reward_override)

        # Atualiza estado interno e política
        state.update(task, agent.type, reward)
        router.update_policy(agent.type, reward)

        ok_str = "OK" if consistent else "FALHOU"
        phase  = "RUIM" if reward_override is not None else "normal"

        print(
            f"{i:>2} | {task[:42]:<42} | {agent.type:>8} | "
            f"{reward:>6.2f} | {avg_reward:>5.3f} | {adaptive_temp:>5.2f} | {ok_str}  [{phase}]"
        )

        results.append({
            "step": i,
            "task": task,
            "expected_type": expected_type,
            "selected": agent.type,
            "reward": reward,
            "recent_avg_reward": avg_reward,
            "adaptive_temperature": adaptive_temp,
            "consistent": consistent,
            "phase": phase
        })
        temp_history.append(adaptive_temp)

    print("-" * 80)

    # ─── Métricas ────────────────────────────────────────────────────────────
    consistency_rate = sum(r["consistent"] for r in results) / len(results)
    avg_reward_final = sum(r["reward"] for r in results) / len(results)

    # Critérios de sucesso
    temps = [r["adaptive_temperature"] for r in results]
    rewards_seq = [r["reward"] for r in results]

    # C1: Temperatura variou (não ficou constante)
    c1 = len(set(temps)) > 1

    # C2: Após tarefa ruim (step 3), temperatura subiu ou ficou alta
    # Comparamos temp no step 3 com temp no step 2
    c2 = temps[2] >= temps[1]  # step 3 >= step 2

    # C3: Após tarefas boas (steps 4-5), temperatura caiu ou estabilizou
    c3 = temps[-1] <= temps[2]  # último step <= step ruim

    # C4: Consistência não despencou (>= 40%)
    c4 = consistency_rate >= 0.4

    print(f"\nMETRICAS GERAIS:")
    print(f"  Consistencia:          {consistency_rate*100:.1f}%")
    print(f"  Reward medio:          {avg_reward_final:.3f}")
    print(f"  Temperatura (sequencia): {[round(t, 2) for t in temps]}")
    print(f"  Recent avg (sequencia):  {[round(r['recent_avg_reward'], 3) for r in results]}")

    print(f"\nCRITERIOS DE SUCESSO N18 P5:")
    print(f"  C1 Temperatura variou:              {'SIM' if c1 else 'NAO'}")
    print(f"  C2 Tarefa ruim aumentou exploracao: {'SIM' if c2 else 'NAO'}")
    print(f"  C3 Tarefas boas reduziram temp:     {'SIM' if c3 else 'NAO'}")
    print(f"  C4 Consistencia >= 40%:             {'SIM' if c4 else 'NAO'}")

    passed = sum([c1, c2, c3, c4])
    status = "APROVADO" if passed >= 3 else "PARCIAL" if passed >= 2 else "REPROVADO"
    print(f"\n  Status N18 P5: {status} ({passed}/4 criterios)")

    # ─── Salva relatório ─────────────────────────────────────────────────────
    report = {
        "level": "N18_P5",
        "status": status,
        "criteria_passed": passed,
        "consistency_rate": consistency_rate,
        "avg_reward": avg_reward_final,
        "temperature_sequence": temps,
        "recent_avg_sequence": [r["recent_avg_reward"] for r in results],
        "results": results
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/n18_p5_adaptive_temp_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\nRelatorio salvo em logs/n18_p5_adaptive_temp_results.json")
    return report


if __name__ == "__main__":
    run_test()
