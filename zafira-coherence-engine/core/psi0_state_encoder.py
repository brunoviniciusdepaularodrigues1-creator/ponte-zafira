<<<<<<< HEAD
"""
psi0_state_encoder.py — N17.3: Encoder Semântico Enriquecido
=============================================================
Evolução do encoder de 5 para 10 dimensões com features semânticas reais.

Dimensões:
  [0]  stage_hash         — identidade ontológica (C/F/A)
  [1]  text_len           — comprimento normalizado
  [2]  llm_rate           — efetividade histórica do LLM
  [3]  v1_rate            — efetividade histórica do V1
  [4]  v2_rate            — efetividade histórica do V2
  [5]  math_density       — densidade de tokens matemáticos
  [6]  logic_density      — densidade de tokens lógicos/filosóficos
  [7]  noise_ratio        — proporção de caracteres não-alfanuméricos
  [8]  lexical_diversity  — diversidade lexical (types/tokens)
  [9]  domain_signal      — sinal de domínio (math=1, logic=0.5, text=0, noise=-1)

Motivação N17.2 → N17.3:
  O encoder anterior usava apenas comprimento e hash do estágio.
  Isso fazia o WorldModel separar textos por FORMA e não por CONTEÚDO.
  As novas features permitem distinguir:
    - "2+2 poeticamente" vs texto literário → math_density diferente
    - "solve x=0" vs "if all cats..." → domain_signal diferente
    - "aaaaaaa" vs "to be or not" → noise_ratio vs lexical_diversity
"""

import hashlib
import re


MATH_TOKENS = {
    "solve", "calculate", "compute", "find", "roots", "sqrt", "sum",
    "multiply", "divide", "subtract", "add", "result", "equals", "equation",
    "algebra", "arithmetic", "integral", "derivative", "matrix", "vector",
    "x", "y", "z",
    "0","1","2","3","4","5","6","7","8","9",
    "mais", "menos", "vezes", "dividido", "soma", "raiz", "calcule", "resolva",
    "dois", "tres", "quatro", "cinco", "seis", "sete", "oito", "nove", "dez",
}

LOGIC_TOKENS = {
    "if", "then", "all", "some", "none", "implies", "therefore", "because",
    "true", "false", "paradox", "contradiction", "tautology", "logic",
    "statement", "premise", "conclusion", "proof", "theorem", "axiom",
    "is", "are", "not", "and", "or", "nor", "but", "however",
    "se", "entao", "todos", "alguns", "nenhum", "portanto", "porque",
    "verdadeiro", "falso", "paradoxo", "logica", "afirmacao",
}


def simple_hash(x):
    return int(hashlib.md5(x.encode()).hexdigest(), 16) % 1000


def _tokenize(text):
    return re.findall(r"[a-zA-Z\u00C0-\u00FF0-9]+|[+\-*/=^]", text.lower())


def _math_density(tokens):
    if not tokens: return 0.0
    return round(sum(1 for t in tokens if t in MATH_TOKENS) / len(tokens), 4)


def _logic_density(tokens):
    if not tokens: return 0.0
    return round(sum(1 for t in tokens if t in LOGIC_TOKENS) / len(tokens), 4)


def _noise_ratio(text):
    if not text: return 0.0
    noise = sum(1 for c in text if not c.isalnum() and not c.isspace())
    return round(noise / (len(text) + 1e-9), 4)


def _lexical_diversity(tokens):
    if not tokens: return 0.0
    return round(len(set(tokens)) / (len(tokens) + 1e-9), 4)


def _domain_signal(math_d, logic_d, noise_r):
    if noise_r > 0.5: return -1.0
    if math_d > 0.15: return round(min(1.0, math_d * 3.0), 4)
    if logic_d > 0.10: return round(0.5 * min(1.0, logic_d * 3.0), 4)
    return 0.0


def encode_state(stage, input_text, history_stats=None):
    """
    Transforma o contexto em vetor de estado de 10 dimensões.
    Compatível com WorldModel N17.2 (state_dim=10).
    """
    if history_stats is None:
        history_stats = {}

    text = input_text or ""
    tokens = _tokenize(text)

    stage_h = round(simple_hash(stage) / 1000.0, 4)
    text_len = round(min(len(text) / 200.0, 1.0), 4)
    llm_rate = round(float(history_stats.get("llm_success", 0.5)), 4)
    v1_rate  = round(float(history_stats.get("v1_success",  0.5)), 4)
    v2_rate  = round(float(history_stats.get("v2_success",  0.5)), 4)

    math_d  = _math_density(tokens)
    logic_d = _logic_density(tokens)
    noise_r = _noise_ratio(text)
    lex_div = _lexical_diversity(tokens)
    domain  = _domain_signal(math_d, logic_d, noise_r)

    return [stage_h, text_len, llm_rate, v1_rate, v2_rate,
            math_d, logic_d, noise_r, lex_div, domain]
=======
import math

def normalize(x):
    """Normaliza vetor para média 0 e desvio 1"""
    n = len(x)
    if n == 0:
        return x
    mean = sum(x) / n
    variance = sum((xi - mean) ** 2 for xi in x) / n
    std = math.sqrt(variance) + 1e-8
    return [(xi - mean) / std for xi in x]

def encode_state(stage, task_input, context):
    """
    N17.3: Normalized Structural Encoder
    Features equilibradas sem dominância
    """
    # Stage hash normalizado
    stage_map = {"C": 0.0, "A": 0.5, "F": 1.0}
    stage_hash = stage_map.get(stage, 0.25)
    
    # Text length com log1p (mata dominância)
    text_len = math.log1p(len(task_input)) if task_input else 0.0
    
    # Taxas dos executores (do contexto)
    llm_rate = context.get("llm_rate", 0.0)
    v1_rate = context.get("v1_rate", 0.0)
    v2_rate = context.get("v2_rate", 0.0)
    
    # Features estruturais minimalistas
    has_digits = 1.0 if any(c.isdigit() for c in task_input) else 0.0
    has_math = 1.0 if any(op in task_input for op in ["+", "-", "*", "/", "=", "^", "**"]) else 0.0
    word_count = math.log1p(len(task_input.split())) if task_input else 0.0
    is_question = 1.0 if any(q in task_input.lower() for q in ["qual", "quanto", "?", "resolve"]) else 0.0
    
    # Diversidade de caracteres
    unique_chars = len(set(task_input)) if task_input else 0
    total_chars = len(task_input) if task_input else 1
    char_div = unique_chars / total_chars
    
    # Vetor completo
    raw_vector = [
        stage_hash,
        text_len,
        llm_rate,
        v1_rate,
        v2_rate,
        has_digits,
        has_math,
        word_count,
        is_question,
        char_div
    ]
    
    # Normalização global
    return normalize(raw_vector)
>>>>>>> 4ee18c6 (N17.3: Normalized structural encoder — features equilibradas, log1p, normalização global)
