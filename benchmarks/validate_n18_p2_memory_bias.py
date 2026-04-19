"""
N18 Passo 2 — Validação do Memory Bias no Router
=================================================
Testa 6 tarefas mistas (2 álgebra, 2 numérico, 2 explicação) e observa:
  1. selected_agent_type
  2. selection_probs
  3. judge_consistency
  4. learning_delta (mudança de policy após reward)
"""

import sys
import os
import json
import random
import numpy as np
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

# ─── Agentes stub para teste isolado ────────────────────────────────────────

class StubAgent:
    def __init__(self, name, agent_type):
        self.name = name
        self.type = agent_type

    def solve(self, task):
        return f"[{self.name}] solução para: {task}"


def make_agents():
    return [
        StubAgent("A1_Symbolic", "symbolic"),
        StubAgent("A2_Numeric",  "numeric"),
        StubAgent("A3_LLM",      "llm"),
    ]


# ─── Judge simples ───────────────────────────────────────────────────────────

def judge(task_category, selected_type):
    """
    Avalia se o agente selecionado é adequado para a categoria.
    Retorna reward e flag de consistência.
    """
    ideal = {
        "algebra":     "symbolic",
        "numeric":     "numeric",
        "explanation": "llm",
    }
    expected = ideal[task_category]
    consistent = selected_type == expected
    # Reward: 1.0 se correto, 0.6 se parcialmente adequado, 0.3 se errado
    if consistent:
        reward = 1.0
    elif selected_type == "llm":
        reward = 0.6   # LLM pode lidar com qualquer coisa, mas não é ideal
    else:
        reward = 0.3
    return reward, consistent


# ─── Tarefas mistas ──────────────────────────────────────────────────────────

TASKS = [
    # (task_text, category)
    ("solve x**2 - 4 = 0",                          "algebra"),
    ("find x where 3x + 6 = 0",                     "algebra"),
    ("calculate 100 - 37",                           "numeric"),
    ("what is 3 * 3",                                "numeric"),
    ("explain why the sky is blue",                  "explanation"),
    ("describe how photosynthesis works in simple terms", "explanation"),
]


# ─── Execução do teste ───────────────────────────────────────────────────────

def run_test():
    from core.psi0_router_v2 import EvolutionaryRouter

    # Usa policy em memória temporária para não contaminar o estado real
    tmp_policy = "/tmp/test_n18_p2_policy.json"
    if os.path.exists(tmp_policy):
        os.remove(tmp_policy)

    agents = make_agents()
    router = EvolutionaryRouter(agents, memory_path=tmp_policy)

    print("=" * 65)
    print("N18 PASSO 2 — VALIDAÇÃO: MEMORY BIAS NO ROUTER")
    print("=" * 65)
    print(f"{'#':>2} | {'Categoria':>12} | {'Selecionado':>12} | {'Probs (sym/num/llm)':>22} | {'Reward':>6} | {'OK?':>4}")
    print("-" * 65)

    results = []
    policy_before = {k: v["score"] for k, v in router.policy.items()}

    for i, (task, category) in enumerate(TASKS, 1):
        # Executa seleção com memory bias
        result = router.select_agent(task)
        agent, probs, meta = result

        # Avalia
        reward, consistent = judge(category, agent.type)

        # Atualiza política (learning)
        router.update_policy(agent.type, reward)

        prob_str = f"[{probs[0]:.2f}/{probs[1]:.2f}/{probs[2]:.2f}]"
        ok_str = "✅" if consistent else "❌"
        print(f"{i:>2} | {category:>12} | {agent.type:>12} | {prob_str:>22} | {reward:>6.2f} | {ok_str:>4}")

        results.append({
            "task": task,
            "category": category,
            "selected": agent.type,
            "probs": probs,
            "reward": reward,
            "consistent": consistent,
            "memory_bias_applied": meta["memory_bias_applied"],
            "preferred_by_memory": meta["preferred_by_memory"],
        })

    policy_after = {k: v["score"] for k, v in router.policy.items()}

    print("-" * 65)

    # ─── Métricas ────────────────────────────────────────────────────────────

    consistency_rate = sum(r["consistent"] for r in results) / len(results)
    avg_reward = sum(r["reward"] for r in results) / len(results)
    memory_bias_used = sum(r["memory_bias_applied"] for r in results)

    # Distribuição por categoria
    dist = {}
    for r in results:
        cat = r["category"]
        sel = r["selected"]
        if cat not in dist:
            dist[cat] = {}
        dist[cat][sel] = dist[cat].get(sel, 0) + 1

    # Learning delta
    learning_delta = {k: round(policy_after[k] - policy_before[k], 4) for k in policy_before}

    print(f"\n📊 MÉTRICAS GERAIS:")
    print(f"  Consistência (agente ideal):  {consistency_rate*100:.1f}%")
    print(f"  Reward médio:                 {avg_reward:.3f}")
    print(f"  Memory bias aplicado:         {memory_bias_used}/{len(results)} tarefas")

    print(f"\n📊 DISTRIBUIÇÃO POR CATEGORIA:")
    for cat, sel_counts in dist.items():
        print(f"  {cat:>12}: {sel_counts}")

    print(f"\n📊 LEARNING DELTA (policy antes → depois):")
    for agent_type in ["symbolic", "numeric", "llm"]:
        before = policy_before[agent_type]
        after  = policy_after[agent_type]
        delta  = learning_delta[agent_type]
        arrow  = "↑" if delta > 0 else ("↓" if delta < 0 else "→")
        print(f"  {agent_type:>10}: {before:.4f} → {after:.4f}  ({arrow} {abs(delta):.4f})")

    # Critérios de sucesso
    print(f"\n📊 CRITÉRIOS DE SUCESSO N18 P2:")
    c1 = any(r["category"] == "explanation" and r["selected"] == "llm" for r in results)
    c2 = any(r["category"] == "numeric" and r["selected"] in ["numeric", "symbolic"] for r in results)
    c3 = len(set(r["selected"] for r in results)) > 1
    c4 = consistency_rate >= 0.5

    print(f"  Explicações → LLM:            {'✅' if c1 else '❌'}")
    print(f"  Numérico → A2/A1:             {'✅' if c2 else '❌'}")
    print(f"  Diversidade viva:             {'✅' if c3 else '❌'}")
    print(f"  Consistency >= 50%:           {'✅' if c4 else '❌'}")

    passed = sum([c1, c2, c3, c4])
    status = "APROVADO" if passed >= 3 else "PARCIAL" if passed >= 2 else "REPROVADO"
    print(f"\n  Status N18 P2: {status} ({passed}/4 critérios)")

    # Salva relatório
    report = {
        "level": "N18_P2",
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
    with open("logs/n18_p2_memory_bias_results.json", "w", encoding="utf-8") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\n📁 Relatório salvo em logs/n18_p2_memory_bias_results.json")
    return report


if __name__ == "__main__":
    random.seed(42)
    np.random.seed(42)
    run_test()
