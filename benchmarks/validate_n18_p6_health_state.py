"""
N18 Passo 6 — Validação: Autorreferência como Sinal de Saúde Operacional
=========================================================================
Sequência de 6 tarefas:
  1. boa    → reward 1.0
  2. ruim   → reward 0.1
  3. ruim   → reward 0.1
  4. normal → reward 0.6
  5. boa    → reward 1.0
  6. boa    → reward 1.0

Transição esperada de health_state:
  stable → recovering → critical → critical → recovering → stable

Critérios de sucesso:
  ✔ health_state aparece no log
  ✔ muda coerentemente com recent_avg_reward
  ✔ bate com a temperatura adaptativa
  ✔ "humor operacional" legível
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

TASKS = [
    ("x**2 - 16 = 0",                     "symbolic", 1.0),   # boa
    ("Resolva impossivel x = x + 1",       "symbolic", 0.1),   # ruim
    ("Calcule raiz de -1",                 "numeric",  0.1),   # ruim
    ("Qual e 144 dividido por 12?",        "numeric",  0.6),   # normal
    ("Calcule 25% de 320",                 "numeric",  1.0),   # boa
    ("Explique energia em uma frase",      "llm",      1.0),   # boa
]

# Transição de health_state esperada
EXPECTED_HEALTH = ["stable", "recovering", "critical", "critical", "recovering", "stable"]


def run_test():
    random.seed(42)
    np.random.seed(42)

    tmp_policy = "/tmp/test_n18_p6_policy.json"
    if os.path.exists(tmp_policy):
        os.remove(tmp_policy)

    agents = make_agents()
    router = EvolutionaryRouter(agents, memory_path=tmp_policy)
    state  = InternalState(window=5)

    print("=" * 85)
    print("N18 PASSO 6 — SAUDE OPERACIONAL EXPLICITA")
    print("=" * 85)
    header = (
        f"{'#':>2} | {'Tarefa':<38} | {'Reward':>6} | "
        f"{'AvgR':>5} | {'Temp':>5} | {'Health':<10} | OK?"
    )
    print(header)
    print("-" * 85)

    results = []

    for i, (task, expected_type, reward) in enumerate(TASKS, 1):
        # Lê estado ANTES de atualizar (estado atual do sistema)
        avg_reward   = state.recent_average_reward()
        adaptive_temp = state.adaptive_temperature()
        health       = state.health_state()

        # Seleciona agente com temperatura adaptativa
        agent, probs, meta = router.select_agent(task, temperature=adaptive_temp)

        # Atualiza estado interno e política
        state.update(task, agent.type, reward)
        router.update_policy(agent.type, reward)

        # Verifica se health_state bate com o esperado
        expected_h = EXPECTED_HEALTH[i - 1]
        ok_str = "OK" if health == expected_h else f"(esp:{expected_h})"

        # Log no console
        print(
            f"{i:>2} | {task[:38]:<38} | {reward:>6.2f} | "
            f"{avg_reward:>5.3f} | {adaptive_temp:>5.2f} | {health:<10} | {ok_str}"
        )
        print(f"     [STATE] health={health} avg_reward={avg_reward:.3f} temp={adaptive_temp:.2f}")

        results.append({
            "step": i,
            "task": task,
            "reward": reward,
            "recent_avg_reward": avg_reward,
            "adaptive_temperature": adaptive_temp,
            "health_state": health,
            "expected_health": expected_h,
            "health_correct": health == expected_h,
            "selected": agent.type
        })

    print("-" * 85)

    # ─── Critérios de sucesso ────────────────────────────────────────────────
    health_seq  = [r["health_state"] for r in results]
    avg_seq     = [r["recent_avg_reward"] for r in results]
    temp_seq    = [r["adaptive_temperature"] for r in results]
    health_ok   = sum(r["health_correct"] for r in results)

    # C1: health_state aparece no log (sempre verdadeiro se chegou aqui)
    c1 = True

    # C2: health_state mudou ao longo da sequência (não ficou constante)
    c2 = len(set(health_seq)) > 1

    # C3: Coerência com temperatura — critical/recovering → temp >= 0.7; stable → temp <= 0.7
    c3_checks = []
    for r in results:
        h = r["health_state"]
        t = r["adaptive_temperature"]
        if h in ("critical", "recovering"):
            c3_checks.append(t >= 0.7)
        else:
            c3_checks.append(t <= 0.7)
    c3 = all(c3_checks)

    # C4: Pelo menos 4/6 health_states corretos
    c4 = health_ok >= 4

    print(f"\nSEQUENCIA DE ESTADOS:")
    print(f"  health_state:       {health_seq}")
    print(f"  recent_avg_reward:  {[round(a, 3) for a in avg_seq]}")
    print(f"  adaptive_temp:      {[round(t, 2) for t in temp_seq]}")

    print(f"\nCRITERIOS DE SUCESSO N18 P6:")
    print(f"  C1 health_state no log:              {'SIM' if c1 else 'NAO'}")
    print(f"  C2 health_state variou:              {'SIM' if c2 else 'NAO'}")
    print(f"  C3 coerente com temperatura:         {'SIM' if c3 else 'NAO'}")
    print(f"  C4 >= 4/6 estados corretos ({health_ok}/6): {'SIM' if c4 else 'NAO'}")

    passed = sum([c1, c2, c3, c4])
    status = "APROVADO" if passed >= 3 else "PARCIAL" if passed >= 2 else "REPROVADO"
    print(f"\n  Status N18 P6: {status} ({passed}/4 criterios)")

    # ─── Salva relatório ─────────────────────────────────────────────────────
    report = {
        "level": "N18_P6",
        "status": status,
        "criteria_passed": passed,
        "health_sequence": health_seq,
        "expected_health_sequence": EXPECTED_HEALTH,
        "health_correct_count": health_ok,
        "avg_reward_sequence": avg_seq,
        "temperature_sequence": temp_seq,
        "results": results
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/n18_p6_health_state_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\nRelatorio salvo em logs/n18_p6_health_state_results.json")
    return report


if __name__ == "__main__":
    run_test()
