"""
N18 Passo 3 — Validação do Classificador de Tarefas
====================================================
Testa a função _detect_task_type() com os 6 casos de referência
e depois executa o teste misto de 6 tarefas para medir o impacto.
"""

import sys
import os
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from core.psi0_router_v2 import EvolutionaryRouter


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


# ─── PARTE 1: Validação isolada da função ────────────────────────────────────

REFERENCE_CASES = [
    ("calculate 100 - 37",              "numeric"),
    ("x**2 - 49 = 0",                   "symbolic"),
    ("Resolva: 6x + 3 = 21",            "symbolic"),
    ("Calcule 12% de 200",              "numeric"),
    ("Explique energia",                "llm"),
    ("Qual e 225 dividido por 15?",     "numeric"),
]


def test_classifier():
    router = EvolutionaryRouter(make_agents())

    print("=" * 70)
    print("PARTE 1 — VALIDACAO ISOLADA DO CLASSIFICADOR")
    print("=" * 70)
    header = f"{'Entrada':<42} | {'Esperado':<10} | {'Obtido':<10} | OK?"
    print(header)
    print("-" * 70)

    all_ok = True
    for task, expected in REFERENCE_CASES:
        got = router._detect_task_type(task)
        ok  = "OK" if got == expected else "FALHOU"
        if got != expected:
            all_ok = False
        print(f"{task:<42} | {expected:<10} | {got:<10} | {ok}")

    print()
    status = "TODOS CORRETOS" if all_ok else "FALHOU EM ALGUM CASO"
    print(f"Resultado: {status}")
    return all_ok


# ─── PARTE 2: Teste misto de 6 tarefas ───────────────────────────────────────

TASKS = [
    ("solve x**2 - 4 = 0",                          "algebra",     "symbolic"),
    ("find x where 3x + 6 = 0",                     "algebra",     "symbolic"),
    ("calculate 100 - 37",                           "numeric",     "numeric"),
    ("what is 3 * 3",                                "numeric",     "numeric"),
    ("explain why the sky is blue",                  "explanation", "llm"),
    ("describe how photosynthesis works simply",     "explanation", "llm"),
]


def judge(expected_type, selected_type):
    consistent = selected_type == expected_type
    if consistent:
        reward = 1.0
    elif selected_type == "llm":
        reward = 0.6
    else:
        reward = 0.3
    return reward, consistent


def test_mixed():
    tmp_policy = "/tmp/test_n18_p3_policy.json"
    if os.path.exists(tmp_policy):
        os.remove(tmp_policy)

    agents = make_agents()
    router = EvolutionaryRouter(agents, memory_path=tmp_policy)

    print()
    print("=" * 70)
    print("PARTE 2 — TESTE MISTO (6 TAREFAS)")
    print("=" * 70)
    header = f"{'#':>2} | {'Categoria':<12} | {'Classificado':<12} | {'Selecionado':<12} | {'Reward':>6} | OK?"
    print(header)
    print("-" * 70)

    results = []
    policy_before = {k: v["score"] for k, v in router.policy.items()}

    for i, (task, category, expected_type) in enumerate(TASKS, 1):
        # Detecta tipo (agora corrigido)
        detected_type = router._detect_task_type(task)

        # Seleciona agente
        agent, probs, meta = router.select_agent(task)

        # Avalia
        reward, consistent = judge(expected_type, agent.type)
        router.update_policy(agent.type, reward)

        ok_str = "OK" if consistent else "FALHOU"
        print(f"{i:>2} | {category:<12} | {detected_type:<12} | {agent.type:<12} | {reward:>6.2f} | {ok_str}")

        results.append({
            "task": task,
            "category": category,
            "detected_type": detected_type,
            "selected": agent.type,
            "reward": reward,
            "consistent": consistent,
            "memory_bias_applied": meta["memory_bias_applied"],
        })

    policy_after = {k: v["score"] for k, v in router.policy.items()}

    print("-" * 70)

    # Métricas
    consistency_rate = sum(r["consistent"] for r in results) / len(results)
    avg_reward       = sum(r["reward"] for r in results) / len(results)
    memory_bias_used = sum(r["memory_bias_applied"] for r in results)
    learning_delta   = {k: round(policy_after[k] - policy_before[k], 4) for k in policy_before}

    # Distribuição por categoria
    dist = {}
    for r in results:
        cat = r["category"]
        sel = r["selected"]
        if cat not in dist:
            dist[cat] = {}
        dist[cat][sel] = dist[cat].get(sel, 0) + 1

    print(f"\nMETRICAS GERAIS:")
    print(f"  Consistencia (agente ideal):  {consistency_rate*100:.1f}%")
    print(f"  Reward medio:                 {avg_reward:.3f}")
    print(f"  Memory bias aplicado:         {memory_bias_used}/{len(results)} tarefas")

    print(f"\nDISTRIBUICAO POR CATEGORIA:")
    for cat, sel_counts in dist.items():
        print(f"  {cat:<14}: {sel_counts}")

    print(f"\nLEARNING DELTA (policy antes -> depois):")
    for agent_type in ["symbolic", "numeric", "llm"]:
        before = policy_before[agent_type]
        after  = policy_after[agent_type]
        delta  = learning_delta[agent_type]
        arrow  = "subiu" if delta > 0 else ("caiu" if delta < 0 else "estavel")
        print(f"  {agent_type:<10}: {before:.4f} -> {after:.4f}  ({arrow} {abs(delta):.4f})")

    # Critérios de sucesso
    c1 = any(r["category"] == "explanation" and r["selected"] == "llm" for r in results)
    c2 = any(r["category"] == "numeric" and r["detected_type"] == "numeric" for r in results)
    c3 = len(set(r["selected"] for r in results)) > 1
    c4 = consistency_rate >= 0.5

    print(f"\nCRITERIOS DE SUCESSO N18 P3:")
    print(f"  Explicacoes -> LLM:           {'SIM' if c1 else 'NAO'}")
    print(f"  Numerico classificado certo:  {'SIM' if c2 else 'NAO'}")
    print(f"  Diversidade viva:             {'SIM' if c3 else 'NAO'}")
    print(f"  Consistency >= 50%:           {'SIM' if c4 else 'NAO'}")

    passed = sum([c1, c2, c3, c4])
    status = "APROVADO" if passed >= 3 else "PARCIAL" if passed >= 2 else "REPROVADO"
    print(f"\n  Status N18 P3: {status} ({passed}/4 criterios)")

    # Salva relatório
    report = {
        "level": "N18_P3",
        "status": status,
        "criteria_passed": passed,
        "consistency_rate": consistency_rate,
        "avg_reward": avg_reward,
        "memory_bias_used": memory_bias_used,
        "distribution_by_category": dist,
        "learning_delta": learning_delta,
        "policy_before": policy_before,
        "policy_after": policy_after,
        "results": results
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/n18_p3_classifier_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\nRelatorio salvo em logs/n18_p3_classifier_results.json")
    return report


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)

    classifier_ok = test_classifier()
    report = test_mixed()
