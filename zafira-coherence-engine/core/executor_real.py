import sympy as sp

def solve_math(input_text):
    try:
        if "=" in input_text:
            x = sp.Symbol('x')
            expr = input_text.replace("resolve", "").strip()

            eq = sp.sympify(expr.split("=")[0]) - sp.sympify(expr.split("=")[1])
            solution = sp.solve(eq, x)

            return float(solution[0]) if solution else None

        # Tenta avaliar numericamente se não houver '='
        clean = input_text.replace("qual é a raiz quadrada de", "sqrt(").replace("raiz quadrada de", "sqrt(").strip()
        # Mapeia sqrt para math.sqrt ou similar se necessário, mas sympy sympify lida bem com sqrt
        if "sqrt" in clean:
            return float(sp.sympify(clean))
        
        return float(eval(input_text))

    except:
        return None
