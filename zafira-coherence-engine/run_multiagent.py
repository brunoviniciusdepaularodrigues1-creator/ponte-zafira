import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

from core.psi0_benchmark_adversarial import ADVERSARIAL_BENCHMARK
from core.psi0_benchmark import BENCHMARK
from core.psi0_controller import AgentController
from core.psi0_judge import AdversarialJudge
from core.psi0_router import classify_task
from collections import defaultdict

print("=" * 60)
print("ZAFIRA — NÍVEL 7.5: MULTI-AGENT COMPETITIVE SYSTEM")
print("=" * 60)

controller = AgentController()
judge = AdversarialJudge()

all_tasks = BENCHMARK + ADVERSARIAL_BENCHMARK

global_wins = defaultdict(int)
global_scores = defaultdict(list)
wins_by_type = defaultdict(lambda: defaultdict(int))

print(f"\nExecutando {len(all_tasks)} tarefas em modo competitivo...\n")

for task in all_tasks:
    task_type = classify_task(task["input"])
    responses, confidences = controller.compete(task["input"])
    scores = judge.evaluate_responses(responses, task["ground_truth"], task.get("alt_truth"))
    winner, winner_info = judge.select_winner(scores)
    controller.update_history(task_type, winner)
    global_wins[winner] += 1
    
    for agent_id, info in scores.items():
        global_scores[agent_id].append(info["score"])
    
    wins_by_type[task_type][winner] += 1
    
    print(f"  Task: {task["id"]} [{task_type}]")
    print(f"    Input: {task["input"]}")
    for agent_id in sorted(scores.keys()):
        info = scores[agent_id]
        marker = " ★" if agent_id == winner else ""
        print(f"    {agent_id} ({controller.agents[agent_id].name}): output={info["output"]} | score={info["score"]:.2f} | rank={info["rank"]}{marker}")
    print(f"    Winner: {winner} ({controller.agents[winner].name})")
    print()

print("=" * 60)
print("RESULTADOS FINAIS — COMPETIÇÃO MULTI-AGENTE")
print("=" * 60)

print("\n--- Vitórias Globais ---")
for agent_id in sorted(global_wins.keys()):
    total = len(all_tasks)
    wins = global_wins[agent_id]
    avg_score = sum(global_scores[agent_id]) / len(global_scores[agent_id]) if global_scores[agent_id] else 0
    print(f"  {agent_id} ({controller.agents[agent_id].name}): {wins}/{total} vitórias | avg_score={avg_score:.3f}")

print("\n--- Vitórias por Tipo de Tarefa ---")
for task_type in sorted(wins_by_type.keys()):
    print(f"  [{task_type}]")
    for agent_id in sorted(wins_by_type[task_type].keys()):
        print(f"    {agent_id}: {wins_by_type[task_type][agent_id]} vitórias")

print("\n--- Agente Preferido por Contexto ---")
for task_type in sorted(controller.win_history.keys()):
    preferred = controller.get_preferred_agent(task_type)
    if preferred:
        print(f"  [{task_type}] → {preferred} ({controller.agents[preferred].name})")

print("\n" + "=" * 60)
print("Competição concluída.")
