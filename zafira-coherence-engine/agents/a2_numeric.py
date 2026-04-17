import numpy as np
import json
import re
import math # Importar o módulo math

class NumericSolver:
    def __init__(self):
        self.name = "A2 - Numeric Solver"
        self.type = "numeric"

    def solve(self, task):
        """
        Tenta resolver a tarefa usando aproximações numéricas e heurísticas rápidas.
        """
        try:
            task_clean = task.lower().replace("solve", "").replace("simplify", "").strip()
            
            # Substitui funções comuns por equivalentes do módulo math
            task_clean = task_clean.replace("sqrt", "math.sqrt").replace("sin", "math.sin").replace("cos", "math.cos")
            task_clean = task_clean.replace("log", "math.log").replace("exp", "math.exp")
            
            # Se houver uma variável 'x', tenta uma busca numérica simples (ex: Newton-Raphson ou busca linear)
            if 'x' in task_clean:
                if '=' in task_clean:
                    lhs, rhs = task_clean.split('=')
                    f_str = f"({lhs.strip()}) - ({rhs.strip()})"
                else:
                    f_str = task_clean
                
                def f(x_val):
                    # Usar um dicionário seguro para eval
                    return eval(f_str.replace('x', f'({x_val})'), {"math": math, "np": np, "__builtins__": {}})
                
                roots = []
                for x_test in np.linspace(-10, 10, 100):
                    try:
                        if abs(f(x_test)) < 0.1:
                            roots.append(round(float(x_test), 4))
                    except (TypeError, NameError): # Captura erros como 'a' não definido em (a+b)**2
                        continue
                
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
                # Para expressões aritméticas sem 'x'
                # Extrai a expressão matemática da string
                # Regex mais abrangente para capturar expressões matemáticas, incluindo funções como sqrt
                match = re.search(r'([\d.+\-*/()\s]+|math\.sqrt\([\d.]+\)|\b(?:sin|cos|tan|log|exp)\b\([\d.+\-*/()]+\))', task_clean)
                if match:
                    expr = match.group(0)
                    try:
                        result = eval(expr, {"math": math, "np": np, "__builtins__": {}})
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
                            "error": f"Erro ao avaliar expressão: {e}",
                            "result": None
                        }
                else:
                    return {
                        "agent": self.name,
                        "status": "error",
                        "error": "Nenhuma expressão numérica encontrada.",
                        "result": None
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
    print(json.dumps(solver.solve("calculate 15 * 3 + 2"), indent=2))
    print(json.dumps(solver.solve("find the square root of 81"), indent=2))
    print(json.dumps(solver.solve("calculate 100 / 4 - 5"), indent=2))
