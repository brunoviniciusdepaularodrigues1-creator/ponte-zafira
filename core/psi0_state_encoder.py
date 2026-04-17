import hashlib

def simple_hash(x):
    """Gera um hash numérico simples para strings."""
    return int(hashlib.md5(x.encode()).hexdigest(), 16) % 1000

def encode_state(stage, input_text, history_stats=None):
    """
    Transforma o contexto simbólico em uma representação vetorial contínua.
    Camada 1: State Encoding.
    """
    if history_stats is None:
        history_stats = {}

    # Normalizações simples
    text_len = len(input_text or "") / 100.0

    # Taxas de sucesso históricas (se disponíveis)
    llm_rate = history_stats.get("llm_success", 0.5)
    v1_rate = history_stats.get("v1_success", 0.5)
    v2_rate = history_stats.get("v2_success", 0.5)

    # Vetor de Estado: [Stage_Hash, Text_Len, LLM_Rate, V1_Rate, V2_Rate]
    return [
        round(simple_hash(stage) / 1000.0, 3),
        round(text_len, 3),
        round(llm_rate, 3),
        round(v1_rate, 3),
        round(v2_rate, 3)
    ]
