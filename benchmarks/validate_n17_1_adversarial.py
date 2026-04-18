"""
N17.1 — Validação Adversarial do Espaço Latente
================================================
Objetivo: Provar que o WorldModel organiza o espaço latente por CONTEÚDO REAL
(semântica) e não por forma superficial (comprimento, palavras-chave, padrão).

Baterias de Teste:
  1. Adversarial Semântico   — "2+2 explicado poeticamente" vs "2+2" puro
  2. Domínio Misto           — matemática disfarçada de narrativa
  3. Paradoxo Lógico         — inputs contraditórios com números
  4. Shuffle de Labels       — mesmo conteúdo, forma diferente
  5. Fora do Padrão          — inputs sem precedente no treino

Métricas:
  - separation_ratio: inter_dist / intra_dist (>1.5 = bom)
  - entropy_stability: variação de entropia sob pressão adversarial
  - cluster_coherence: consistência dos clusters após inputs hostis
  - collapse_detected: se o espaço latente colapsou (intra ≈ inter)
"""

import sys
import os
import numpy as np
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
from core.world_model import WorldModel
sys.path.append(str(Path(__file__).parent.parent / 'zafira-coherence-engine'))
from core.psi0_state_encoder import encode_state

# ─────────────────────────────────────────────
# ENCODER DE ESTADO PARA INPUTS TEXTUAIS
# ─────────────────────────────────────────────

def text_to_state(text, stage="F", history=None):
    """Converte texto em vetor de estado via psi0_state_encoder."""
    history = history or {"llm_success": 0.5, "v1_success": 0.5, "v2_success": 0.5}
    base = encode_state(stage, text, history)
    # Expande para 10 dims (padrão do WorldModel N17)
    while len(base) < 10:
        base.append(0.0)
    arr = np.array(base[:10], dtype=float)
    norm = np.linalg.norm(arr) + 1e-9
    return arr / norm


# ─────────────────────────────────────────────
# BATERIAS DE TESTE
# ─────────────────────────────────────────────

ADVERSARIAL_BATCHES = {

    # BATERIA 1: Adversarial Semântico
    # Matemática pura vs matemática disfarçada de poesia
    "adversarial_semantic": {
        "cluster_A": [
            "2 + 2",
            "solve 4 + 4",
            "calculate 10 / 2",
            "what is 3 * 3",
            "compute 100 - 37",
        ],
        "cluster_B": [
            "dois mais dois explicado poeticamente como o encontro de almas",
            "a soma de quatro e quatro narrada como uma história de amor",
            "dez dividido por dois descrito como uma jornada espiritual",
            "três vezes três contado como um poema sobre a natureza",
            "cem menos trinta e sete como uma metáfora de perda",
        ],
        "expected": "SAME_CLUSTER",  # Ambos são matemática — devem ficar próximos
        "description": "Matemática pura vs matemática em linguagem poética"
    },

    # BATERIA 2: Domínio Misto
    # Álgebra vs raciocínio lógico — devem ficar SEPARADOS
    "domain_mixed": {
        "cluster_A": [
            "solve x**2 - 4 = 0",
            "find x where 3x + 6 = 0",
            "resolve x**3 - 8 = 0",
            "calculate roots of x**2 + 5x + 6",
            "solve 2x - 10 = 0",
        ],
        "cluster_B": [
            "if all cats are animals and Felix is a cat, is Felix an animal?",
            "all humans are mortal, Socrates is human, therefore?",
            "if A implies B and B implies C, does A imply C?",
            "is a statement that contradicts itself always false?",
            "can something be true and false at the same time?",
        ],
        "expected": "DIFFERENT_CLUSTERS",  # Álgebra vs lógica — devem ficar separados
        "description": "Álgebra simbólica vs raciocínio lógico puro"
    },

    # BATERIA 3: Paradoxo Lógico com Números
    # Inputs que misturam forma matemática com conteúdo contraditório
    "logical_paradox": {
        "cluster_A": [
            "1 = 1",
            "2 = 2",
            "true is true",
            "0 = 0",
            "x = x for all x",
        ],
        "cluster_B": [
            "this statement is false",
            "1 = 2 if you believe hard enough",
            "the set of all sets that do not contain themselves",
            "I always lie — is this sentence true?",
            "infinity plus one equals infinity, but also equals infinity minus one",
        ],
        "expected": "DIFFERENT_CLUSTERS",  # Tautologias vs paradoxos — devem separar
        "description": "Tautologias matemáticas vs paradoxos lógicos"
    },

    # BATERIA 4: Shuffle de Labels (Forma vs Conteúdo)
    # Mesmo conteúdo matemático, formas completamente diferentes
    "label_shuffle": {
        "cluster_A": [
            "what is the square root of 16?",
            "compute sqrt(16)",
            "√16 = ?",
            "find the value of 16^0.5",
            "sixteen to the power of one half",
        ],
        "cluster_B": [
            "what is the capital of France?",
            "who wrote Hamlet?",
            "when did World War II end?",
            "what is the speed of light?",
            "name the largest planet in the solar system",
        ],
        "expected": "DIFFERENT_CLUSTERS",  # Matemática vs conhecimento geral — devem separar
        "description": "Raiz quadrada (formas variadas) vs conhecimento geral"
    },

    # BATERIA 5: Fora do Padrão (Out-of-Distribution)
    # Inputs sem precedente — o sistema não deve colapsar
    "out_of_distribution": {
        "cluster_A": [
            "aaaaaaaaaaaaaaaaaaaaaaaaaaaa",
            "!@#$%^&*()_+{}|:<>?",
            "                    ",
            "1111111111111111111111111111",
            "ZZZZZZZZZZZZZZZZZZZZZZZZZZZZ",
        ],
        "cluster_B": [
            "the quick brown fox jumps over the lazy dog",
            "to be or not to be that is the question",
            "it was the best of times it was the worst of times",
            "in the beginning god created the heavens and the earth",
            "four score and seven years ago our fathers brought forth",
        ],
        "expected": "DIFFERENT_CLUSTERS",  # Ruído vs texto coerente — devem separar
        "description": "Ruído puro vs texto literário coerente"
    },
}


# ─────────────────────────────────────────────
# EXECUTOR DA VALIDAÇÃO
# ─────────────────────────────────────────────

def run_adversarial_batch(wm, batch_name, batch_data, n_train=50):
    """Executa uma bateria adversarial e retorna métricas de separação."""
    cluster_A = batch_data["cluster_A"]
    cluster_B = batch_data["cluster_B"]
    expected = batch_data["expected"]

    # Treino: expõe o WorldModel aos dois clusters
    for _ in range(n_train):
        # Treina intra-cluster A
        for i in range(len(cluster_A) - 1):
            s = text_to_state(cluster_A[i])
            ns = text_to_state(cluster_A[i + 1])
            wm.update(s, "A1", ns, 0.9)

        # Treina intra-cluster B
        for i in range(len(cluster_B) - 1):
            s = text_to_state(cluster_B[i])
            ns = text_to_state(cluster_B[i + 1])
            wm.update(s, "A2", ns, 0.7)

    # Codifica todos os estados
    z_A = [wm.encode(text_to_state(t)) for t in cluster_A]
    z_B = [wm.encode(text_to_state(t)) for t in cluster_B]

    # Métricas de separação
    intra_dists = []
    for i in range(len(z_A)):
        for j in range(i + 1, len(z_A)):
            intra_dists.append(np.linalg.norm(z_A[i] - z_A[j]))
    for i in range(len(z_B)):
        for j in range(i + 1, len(z_B)):
            intra_dists.append(np.linalg.norm(z_B[i] - z_B[j]))

    inter_dists = []
    for za in z_A:
        for zb in z_B:
            inter_dists.append(np.linalg.norm(za - zb))

    avg_intra = float(np.mean(intra_dists)) if intra_dists else 0.0
    avg_inter = float(np.mean(inter_dists)) if inter_dists else 0.0
    sep_ratio = avg_inter / (avg_intra + 1e-9)

    # Entropia do espaço latente (variância dos vetores)
    all_z = z_A + z_B
    z_matrix = np.array(all_z)
    entropy_proxy = float(np.mean(np.var(z_matrix, axis=0)))

    # Colapso detectado: intra ≈ inter
    collapse = abs(avg_intra - avg_inter) < 0.01

    # Resultado esperado vs obtido
    if expected == "SAME_CLUSTER":
        passed = sep_ratio < 2.0   # Devem estar próximos
    else:
        passed = sep_ratio > 1.5   # Devem estar separados

    return {
        "batch": batch_name,
        "description": batch_data["description"],
        "expected": expected,
        "avg_intra_dist": round(avg_intra, 4),
        "avg_inter_dist": round(avg_inter, 4),
        "separation_ratio": round(sep_ratio, 4),
        "entropy_proxy": round(entropy_proxy, 4),
        "collapse_detected": collapse,
        "passed": passed,
        "avg_contrast_loss": round(wm.get_avg_contrast_loss(), 4),
    }


def run_n17_1_adversarial():
    print("=" * 60)
    print("N17.1 — VALIDAÇÃO ADVERSARIAL DO ESPAÇO LATENTE")
    print("=" * 60)

    results = []
    passed_count = 0

    for batch_name, batch_data in ADVERSARIAL_BATCHES.items():
        # Novo WorldModel por bateria para isolamento
        wm = WorldModel(state_dim=10, latent_dim=2, gamma=0.5)
        print(f"\n🧪 Bateria: {batch_name}")
        print(f"   {batch_data['description']}")

        result = run_adversarial_batch(wm, batch_name, batch_data)
        results.append(result)

        status = "✅ PASSOU" if result["passed"] else "❌ FALHOU"
        if result["passed"]:
            passed_count += 1

        print(f"   Intra-dist: {result['avg_intra_dist']:.4f} | Inter-dist: {result['avg_inter_dist']:.4f}")
        print(f"   Separation Ratio: {result['separation_ratio']:.4f} | Entropy: {result['entropy_proxy']:.4f}")
        print(f"   Colapso: {result['collapse_detected']} | Contrast Loss: {result['avg_contrast_loss']:.4f}")
        print(f"   {status}")

    # Relatório final
    total = len(ADVERSARIAL_BATCHES)
    robustness_score = passed_count / total

    print("\n" + "=" * 60)
    print(f"RESULTADO FINAL N17.1")
    print(f"  Baterias Passadas: {passed_count}/{total}")
    print(f"  Score de Robustez: {robustness_score:.2%}")

    if robustness_score >= 0.8:
        verdict = "ESPAÇO LATENTE ROBUSTO — organiza por conteúdo real"
        ready_for_n18 = True
    elif robustness_score >= 0.6:
        verdict = "ESPAÇO LATENTE PARCIALMENTE ROBUSTO — ajustes necessários"
        ready_for_n18 = False
    else:
        verdict = "ESPAÇO LATENTE FRÁGIL — organiza por forma superficial"
        ready_for_n18 = False

    print(f"  Veredito: {verdict}")
    print(f"  Pronto para N18: {ready_for_n18}")
    print("=" * 60)

    report = {
        "level": "N17.1",
        "status": "ADVERSARIAL_VALIDATION",
        "batches_passed": passed_count,
        "total_batches": total,
        "robustness_score": round(robustness_score, 4),
        "verdict": verdict,
        "ready_for_n18": ready_for_n18,
        "batch_results": results
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/n17_1_adversarial_results.json", "w") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\n📁 Resultados salvos em logs/n17_1_adversarial_results.json")
    return report


if __name__ == "__main__":
    run_n17_1_adversarial()
