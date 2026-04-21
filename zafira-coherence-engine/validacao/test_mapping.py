import sys
import os
sys.path.append(os.getcwd())

from core_v2.psi0_router_v2 import EvolutionaryRouter
from agents.a1_symbolic import SymbolicSolver
from agents.a2_numeric import NumericSolver
from agents.a3_llm import LLMSolver

def test_mapping():
    agents = [SymbolicSolver(), NumericSolver(), LLMSolver()]
    router = EvolutionaryRouter(agents)
    
    test_cases = [
        ("calculate 100 - 37", "numeric"),
        ("Qual é 225 dividido por 15?", "numeric"),
        ("x**2 - 49 = 0", "symbolic"),
        ("Explique energia", "llm")
    ]
    
    print("--- VALIDAÇÃO DE MAPEAMENTO (N18 PASSO 4) ---")
    print(f"{'Tarefa':<30} | {'Esperado':<10} | {'Detectado':<10} | {'Status'}")
    print("-" * 65)
    
    all_pass = True
    for task, expected in test_cases:
        detected = router._detect_task_type(task)
        status = "PASS" if detected == expected else "FAIL"
        if status == "FAIL": all_pass = False
        print(f"{task:<30} | {expected:<10} | {detected:<10} | {status}")
    
    print("-" * 65)
    if all_pass:
        print("Resultado: TODOS OS TESTES PASSARAM")
    else:
        print("Resultado: FALHA EM ALGUNS TESTES")

if __name__ == "__main__":
    test_mapping()
