import random

def mutate_weight(base, strength=0.1):
    # Mutação controlada: adiciona uma variação aleatória ao peso base
    return max(0.0, base + random.uniform(-strength, strength))

def create_variant(config):
    # Gera uma nova variante de configuração baseada em uma configuração de sucesso
    return {
        "length_weight": mutate_weight(config.get("length_weight", 0.3)),
        "word_weight": mutate_weight(config.get("word_weight", 0.3)),
        "complexity_weight": mutate_weight(config.get("complexity_weight", 0.4))
    }
