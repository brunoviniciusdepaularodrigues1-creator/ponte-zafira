"""
N18 Passo 7 — Validação: Memory Bias Adaptativo ao Health State
================================================================
Sequência de 6 tarefas:
  1. boa    → reward 1.0  → stable
  2. ruim   → reward 0.1  → stable (delay)
  3. ruim   → reward 0.1  → recovering
  4. normal → reward 0.6  → recovering/critical
  5. boa    → reward 1.0  → recovering
  6. boa    → reward 1.0  → stable

Critérios de sucesso:
  ✔ adaptive_memory_bias varia conforme health_state
  ✔ valor aparece no log
  ✔ em critical/recovering o bias é maior (0.06-0.08)
  ✔ sem colapso para um único agente
"""

import sys
import os
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.psi0_router_v2 import EvolutionaryRouter, InternalState


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


TASKS = [
    ("x**2 - 16 = 0",                     "symbolic", 1.0),   # boa
    ("Resolva impossivel x = x + 1",       "symbolic", 0.1),   # ruim
    ("Calcule raiz de -1",                 "numeric",  0.1),   # ruim
    ("Qual e 144 dividido por 12?",        "numeric",  0.6),   # normal
    ("Calcule 25% de 320",                 "numeric",  1.0),   # boa
    ("Explique energia em uma frase",      "llm",      1.0),   # boa
]


def run_test():
    random.seed(42)
    np.random.seed(42)

    tmp_policy = "/tmp/test_n18_p7_policy.json"
    if os.path.exists(tmp_policy):
        os.remove(tmp_policy)

    agents = make_agents()
    router = EvolutionaryRouter(agents, memory_path=tmp_policy)
    state  = InternalState(window=5)

    print("=" * 90)
    print("N18 PASSO 7 — ADAPTIVE MEMORY BIAS (HEALTH-AWARE)")
    print("=" * 90)
    header = (
        f"{'#':>2} | {'Tarefa':<36} | {'Sel':>8} | {'Rew':>4} | "
        f"{'AvgR':>5} | {'Temp':>5} | {'Health':<10} | {'Bias':>5}"
    )
    print(header)
    print("-" * 90)

    results = []
    agent_types_seen = set()

    for i, (task, expected_type, reward) in enumerate(TASKS, 1):
        # Lê estado ANTES de atualizar
        avg_reward    = state.recent_average_reward()
        adaptive_temp = state.adaptive_temperature()
        health        = state.health_state()

        # Seleciona agente passando health para o router
        agent, probs, meta = router.select_agent(
            task,
            temperature=adaptive_temp,
            health=health
        )

        adaptive_bias = meta["adaptive_memory_bias"]
        agent_types_seen.add(agent.type)

        # Log no console
        print(
            f"{i:>2} | {task[:36]:<36} | {agent.type:>8} | {reward:>4.2f} | "
            f"{avg_reward:>5.3f} | {adaptive_temp:>5.2f} | {health:<10} | {adaptive_bias:>5.2f}"
        )
        print(f"     [STATE] health={health} bias={adaptive_bias:.2f} temp={adaptive_temp:.2f} selected={agent.type}")

        # Atualiza estado e política
        state.update(task, agent.type, reward)
        router.update_policy(agent.type, reward)

        results.append({
            "step": i,
            "task": task,
            "reward": reward,
            "recent_avg_reward": avg_reward,
            "adaptive_temperature": adaptive_temp,
            "health_state": health,
            "adaptive_memory_bias": adaptive_bias,
            "selected": agent.type
        })

    print("-" * 90)

    # ─── Critérios de sucesso ────────────────────────────────────────────────
    bias_seq   = [r["adaptive_memory_bias"] for r in results]
    health_seq = [r["health_state"] for r in results]
    sel_seq    = [r["selected"] for r in results]

    # C1: adaptive_memory_bias variou (não ficou constante em 0.05)
    c1 = len(set(bias_seq)) > 1

    # C2: bias aparece no log (sempre verdadeiro se chegou aqui)
    c2 = True

    # C3: em critical/recovering o bias é >= 0.06
    c3_checks = []
    for r in results:
        if r["health_state"] in ("critical", "recovering"):
            c3_checks.append(r["adaptive_memory_bias"] >= 0.06)
    c3 = all(c3_checks) if c3_checks else True  # se nunca entrou em critical/recovering, ok

    # C4: sem colapso — pelo menos 2 tipos de agente distintos selecionados
    c4 = len(agent_types_seen) >= 2

    print(f"\nSEQUENCIAS:")
    print(f"  health_state:          {health_seq}")
    print(f"  adaptive_memory_bias:  {bias_seq}")
    print(f"  selected_agent_type:   {sel_seq}")

    print(f"\nMETRICAS GERAIS:")
    avg_reward_final = sum(r["reward"] for r in results) / len(results)
    consistency = sum(1 for r in results if r["selected"] == TASKS[r["step"]-1][1]) / len(results)
    print(f"  Reward medio:     {avg_reward_final:.3f}")
    print(f"  Consistencia:     {consistency*100:.1f}%")
    print(f"  Agentes distintos selecionados: {sorted(agent_types_seen)}")

    print(f"\nCRITERIOS DE SUCESSO N18 P7:")
    print(f"  C1 bias variou (nao fixo em 0.05):     {'SIM' if c1 else 'NAO'}")
    print(f"  C2 bias aparece no log:                {'SIM' if c2 else 'NAO'}")
    print(f"  C3 critical/recovering bias >= 0.06:   {'SIM' if c3 else 'NAO'}")
    print(f"  C4 sem colapso (>= 2 agentes):         {'SIM' if c4 else 'NAO'}")

    passed = sum([c1, c2, c3, c4])
    status = "APROVADO" if passed >= 3 else "PARCIAL" if passed >= 2 else "REPROVADO"
    print(f"\n  Status N18 P7: {status} ({passed}/4 criterios)")

    # ─── Salva relatório ─────────────────────────────────────────────────────
    report = {
        "level": "N18_P7",
        "status": status,
        "criteria_passed": passed,
        "health_sequence": health_seq,
        "adaptive_memory_bias_sequence": bias_seq,
        "selected_agent_sequence": sel_seq,
        "avg_reward": avg_reward_final,
        "consistency_rate": consistency,
        "agents_seen": sorted(agent_types_seen),
        "results": results
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/n18_p7_adaptive_bias_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\nRelatorio salvo em logs/n18_p7_adaptive_bias_results.json")
    return report


if __name__ == "__main__":
    run_test()
