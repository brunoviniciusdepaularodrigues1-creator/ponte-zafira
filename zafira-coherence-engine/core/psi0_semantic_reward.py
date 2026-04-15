import sympy as sp

def semantic_evaluate(output, ground_truth, alt_truth=None, tolerance=0.01):
    """
    Avalia o output contra ground_truth de forma semântica real.
    Retorna score entre 0.0 e 1.0
    """
    if output is None:
        return 0.0
    
    # Comparação exata
    if output == ground_truth:
        return 1.0
    
    # Comparação numérica com tolerância
    try:
        if abs(float(output) - float(ground_truth)) < tolerance:
            return 1.0
    except (ValueError, TypeError):
        pass
    
    # Comparação simbólica via SymPy
    try:
        diff = sp.simplify(sp.sympify(output) - sp.sympify(ground_truth))
        if diff == 0:
            return 1.0
    except:
        pass
    
    # Respostas alternativas válidas (score parcial)
    if alt_truth:
        for alt in alt_truth:
            try:
                if abs(float(output) - float(alt)) < tolerance:
                    return 0.8
            except (ValueError, TypeError):
                pass
            try:
                diff = sp.simplify(sp.sympify(output) - sp.sympify(alt))
                if diff == 0:
                    return 0.8
            except:
                pass
    
    # Output numérico próximo mas não exato
    try:
        error = abs(float(output) - float(ground_truth))
        if error < 1.0:
            return max(0.1, 1.0 - error)  # score proporcional ao erro
    except (ValueError, TypeError):
        pass
    
    return 0.0
