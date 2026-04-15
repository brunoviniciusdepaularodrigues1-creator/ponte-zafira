from core.executor_real import solve_math

def execute(action, input_text):
    if action == "A1":
        return solve_math(input_text)

    if action == "A2":
        try:
            # Tenta resolver numericamente
            clean = input_text.replace("resolve", "").strip()
            if "=" in clean:
                # Tenta resolver equação simples numericamente (fallback simples)
                parts = clean.split("=")
                # Aqui o numeric_solver é mais limitado propositalmente para testar especialização
                return float(eval(parts[1].strip()))
            return float(eval(clean))
        except:
            return None

    if action == "A3":
        # A3 (LLM) está desabilitado propositalmente para forçar o agente a aprender A1/A2
        return None

    return None
