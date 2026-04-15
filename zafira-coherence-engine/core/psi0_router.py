def classify_task(input_text):
    """
    Classifica o tipo de tarefa para routing inteligente.
    Retorna: 'algebra', 'arithmetic', 'reasoning', 'unknown'
    """
    input_lower = input_text.lower()
    
    if "resolve" in input_lower or "=" in input_lower:
        if "x" in input_lower or "**" in input_lower or "^" in input_lower:
            return "algebra"
        return "algebra"
    
    # Operações aritméticas simples
    operators = ["+", "-", "*", "/"]
    has_operator = any(op in input_text for op in operators)
    has_only_numbers = all(c.isdigit() or c in " .+-*/()" for c in input_text.strip())
    
    if has_operator and has_only_numbers:
        return "arithmetic"
    
    if has_operator:
        return "arithmetic"
    
    return "reasoning"


def get_strategy_bias(task_type):
    """
    Retorna bias de estratégia baseado no tipo de tarefa.
    Usado para influenciar a decisão do Actor.
    """
    strategies = {
        "algebra": {"A1": 0.7, "A2": 0.2, "A3": 0.1},
        "arithmetic": {"A1": 0.3, "A2": 0.6, "A3": 0.1},
        "reasoning": {"A1": 0.2, "A2": 0.1, "A3": 0.7},
        "unknown": {"A1": 0.33, "A2": 0.33, "A3": 0.34}
    }
    return strategies.get(task_type, strategies["unknown"])
