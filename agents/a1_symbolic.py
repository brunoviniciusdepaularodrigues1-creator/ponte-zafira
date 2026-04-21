import sympy
import json

class SymbolicSolver:
    def __init__(self):
        self.name = "A1 - Symbolic Solver"
        self.type = "symbolic"

    def solve(self, task):
        """
        Tenta resolver a tarefa usando SymPy para manipulação simbólica.
        """
        try:
            # Tenta interpretar a tarefa como uma expressão matemática
            # Exemplo de tarefa: "solve x**2 - 4 = 0" ou "simplify (x+1)**2"
            task_clean = task.lower().replace("solve", "").replace("simplify", "").strip()
            
            if "=" in task_clean:
                lhs, rhs = task_clean.split("=")
                expr = sympy.sympify(lhs.strip()) - sympy.sympify(rhs.strip())
                solution = sympy.solve(expr)
                return {
                    "agent": self.name,
                    "status": "success",
                    "result": str(solution),
                    "method": "sympy.solve"
                }
            else:
                expr = sympy.sympify(task_clean)
                result = sympy.simplify(expr)
                return {
                    "agent": self.name,
                    "status": "success",
                    "result": str(result),
                    "method": "sympy.simplify"
                }
        except Exception as e:
            return {
                "agent": self.name,
                "status": "error",
                "error": str(e),
                "result": None
            }

if __name__ == "__main__":
    solver = SymbolicSolver()
    print(json.dumps(solver.solve("x**2 - 9 = 0"), indent=2))
