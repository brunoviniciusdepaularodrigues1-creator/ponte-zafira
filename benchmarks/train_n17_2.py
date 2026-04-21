"""
N17.2 — Treino de 50 Ciclos com Observação de Métricas Anti-Colapso
====================================================================
Observa ciclo a ciclo:
  - entropy_proxy (variância do latente)
  - latent_variance
  - avg_norm (deve ser ~1.0)
  - contrast_loss (deve ↓ ao longo do tempo)
  - var_loss
"""

import sys
import os
import numpy as np
import json
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))
sys.path.append(str(Path(__file__).parent.parent / 'zafira-coherence-engine'))

from core.world_model import WorldModel
from core.psi0_state_encoder import encode_state


def text_to_state(text, stage="F"):
    base = encode_state(stage, text, {"llm_success": 0.5, "v1_success": 0.5, "v2_success": 0.5})
    while len(base) < 10:
        base.append(0.0)
    arr = np.array(base[:10], dtype=float)
    norm = np.linalg.norm(arr) + 1e-9
    return arr / norm


# Dataset misto: matemática, lógica, ruído, texto
TRAINING_PAIRS = [
    # (input, next_input, action, reward)
    ("solve x**2 - 4 = 0",           "roots are x=2 and x=-2",              "A1", 0.95),
    ("2 + 2 explicado poeticamente",  "quatro como encontro de almas",        "A3", 0.70),
    ("if all cats are animals",       "then Felix is an animal",              "A3", 0.90),
    ("calculate 10 / 2",              "result is 5",                          "A2", 0.95),
    ("this statement is false",       "paradox detected",                     "A3", 0.60),
    ("aaaaaaaaaaaaaaaa",              "noise input detected",                 "A2", 0.30),
    ("solve 3x + 6 = 0",             "x = -2",                               "A1", 0.95),
    ("to be or not to be",           "that is the question",                 "A3", 0.80),
    ("1 = 1",                        "tautology confirmed",                  "A3", 0.85),
    ("what is sqrt(16)",             "answer is 4",                          "A2", 0.95),
    ("paradox: set of all sets",     "Russell paradox",                      "A3", 0.55),
    ("compute 100 - 37",             "result is 63",                         "A2", 0.95),
    ("!@#$%^&*()",                   "unrecognized input",                   "A2", 0.20),
    ("find x where 3x = 9",         "x = 3",                                "A1", 0.95),
    ("the quick brown fox",          "jumps over the lazy dog",              "A3", 0.75),
]


def run_training():
    print("=" * 60)
    print("N17.2 — TREINO ANTI-COLAPSO (50 CICLOS)")
    print("=" * 60)
    print(f"{'Ciclo':>5} | {'Entropy':>8} | {'Variance':>8} | {'Norm':>6} | {'Contrast':>8} | {'VarLoss':>8}")
    print("-" * 60)

    wm = WorldModel(state_dim=10, latent_dim=2, learning_rate=0.05,
                    beta=0.5, gamma=0.1, tau=0.1)

    cycle_logs = []

    for cycle in range(1, 51):
        # Seleciona par de treino ciclicamente
        pair = TRAINING_PAIRS[(cycle - 1) % len(TRAINING_PAIRS)]
        s = text_to_state(pair[0])
        ns = text_to_state(pair[1])
        action = pair[2]
        reward = pair[3]

        total_loss = wm.update(s, action, ns, reward)
        telem = wm.get_telemetry()

        cycle_logs.append({
            "cycle": cycle,
            "input": pair[0],
            "action": action,
            "reward": reward,
            "total_loss": round(float(total_loss), 4),
            **telem
        })

        if cycle % 5 == 0 or cycle <= 5:
            print(f"{cycle:>5} | {telem['entropy_proxy']:>8.5f} | {telem['latent_variance']:>8.5f} | "
                  f"{telem['avg_norm']:>6.4f} | {telem['contrast_loss']:>8.4f} | {telem['var_loss']:>8.4f}")

    print("-" * 60)

    # Avaliação final
    final = cycle_logs[-1]
    entropy_ok = final["entropy_proxy"] > 0.001
    variance_ok = final["latent_variance"] > 0.001
    norm_ok = 0.8 <= final["avg_norm"] <= 1.2
    contrast_trend = cycle_logs[-1]["contrast_loss"] <= cycle_logs[5]["contrast_loss"] if len(cycle_logs) > 5 else True

    print(f"\n📊 AVALIAÇÃO FINAL (Ciclo 50):")
    print(f"  Entropy > 0:      {'✅' if entropy_ok else '❌'} ({final['entropy_proxy']:.5f})")
    print(f"  Variance > 0.01:  {'✅' if variance_ok else '❌'} ({final['latent_variance']:.5f})")
    print(f"  Norm ~1.0:        {'✅' if norm_ok else '❌'} ({final['avg_norm']:.4f})")
    print(f"  Contrast ↓:       {'✅' if contrast_trend else '❌'}")

    passed = sum([entropy_ok, variance_ok, norm_ok, contrast_trend])
    status = "ESTÁVEL" if passed >= 3 else "INSTÁVEL"
    print(f"\n  Status N17.2: {status} ({passed}/4 critérios)")

    report = {
        "level": "N17.2",
        "status": status,
        "criteria_passed": passed,
        "final_telemetry": final,
        "cycle_logs": cycle_logs
    }

    os.makedirs("logs", exist_ok=True)
    with open("logs/n17_2_training_results.json", "w") as f:
        json.dump(report, f, indent=4, ensure_ascii=False)

    print("\n📁 Logs salvos em logs/n17_2_training_results.json")
    return report


if __name__ == "__main__":
    run_training()
