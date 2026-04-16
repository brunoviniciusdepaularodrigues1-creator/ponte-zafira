import numpy as np
import json
import re

class NumericSolver:
    def __init__(self):
        self.name = "A2 - Numeric Solver"
        self.type = "numeric"

    def solve(self, task):
        """
        Tenta resolver a tarefa usando aproximações numéricas e heurísticas rápidas.
        """
        try:
            # Tenta encontrar números e operações básicas
            # Exemplo: "sqrt(16) + 2 * 5"
            task_clean = task.lower().replace("solve", "").replace("simplify", "").strip()
            
            # Heurística simples para expressões aritméticas
            # Substitui funções comuns por numpy equivalents
            task_clean = task_clean.replace("sqrt", "np.sqrt").replace("sin", "np.sin").replace("cos", "np.cos")
            
            # Se houver uma variável 'x', tenta uma busca numérica simples (ex: Newton-Raphson ou busca linear)
            if 'x' in task_clean:
                # Exemplo: x**2 - 4 = 0
                if '=' in task_clean:
                    lhs, rhs = task_clean.split('=')
                    f_str = f"({lhs.strip()}) - ({rhs.strip()})"
                else:
                    f_str = task_clean
                
                # Define uma função f(x)
                def f(x_val):
                    return eval(f_str.replace('x', f'({x_val})'), {"np": np, "__builtins__": {}})
                
                # Busca linear simples em um intervalo para encontrar uma raiz
                roots = []
                for x_test in np.linspace(-100, 100, 1000):
                    if abs(f(x_test)) < 0.1:
                        roots.append(round(float(x_test), 4))
                
                # Remove duplicatas próximas
                unique_roots = []
                if roots:
                    unique_roots.append(roots[0])
                    for r in roots[1:]:
                        if all(abs(r - ur) > 0.1 for ur in unique_roots):
                            unique_roots.append(r)

                return {
                    "agent": self.name,
                    "status": "success",
                    "result": str(unique_roots),
                    "method": "numeric_search"
                }
            else:
                # Apenas cálculo direto
                result = eval(task_clean, {"np": np, "__builtins__": {}})
                return {
                    "agent": self.name,
                    "status": "success",
                    "result": str(result),
                    "method": "direct_eval"
                }
        except Exception as e:
            return {
                "agent": self.name,
                "status": "error",
                "error": str(e),
                "result": None
            }

if __name__ == "__main__":
    solver = NumericSolver()
    print(json.dumps(solver.solve("x**2 - 4 = 0"), indent=2))
    print(json.dumps(solver.solve("sqrt(16) + 10"), indent=2))
