import os
import sys

# Adiciona a raiz do projeto ao sys.path para permitir imports de core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.a1_symbolic import SymbolicSolver
from agents.a2_numeric import NumericSolver
from agents.a3_llm import LLMSolver

# Instancia os agentes
symbolic_solver = SymbolicSolver()
numeric_solver = NumericSolver()
llm_solver = LLMSolver()

def execute(action, input_text):
    if action == "A1":
        result = symbolic_solver.solve(input_text)
        return result.get("result")

    if action == "A2":
        result = numeric_solver.solve(input_text)
        return result.get("result")

    if action == "A3":
        result = llm_solver.solve(input_text)
        return result.get("result")

    return None
