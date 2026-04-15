def format_output(input_text, state):
    stage_map = {
        "C": "Entrada caótica, precisa de organização",
        "F": "Organizando estrutura do conteúdo",
        "A": "Pronto para execução",
        "V": "Validando consistência",
        "L": "Aprendizado consolidado"
    }

    return {
        "input": input_text,
        "stage": state["stage"],
        "interpretation": stage_map[state["stage"]],
        "coherence": round(state["C"], 3),
        "structure": round(state["G"], 3),
        "variation": round(state["V"], 3)
    }
