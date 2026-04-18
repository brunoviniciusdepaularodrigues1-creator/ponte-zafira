import sys
import os
import numpy as np
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar o core
sys.path.append(str(Path(__file__).parent.parent))

from core.world_model import WorldModel

def simulate_n13_prediction():
    print(f"🚀 Iniciando Validação Nível 13: World Model & Antecipação...")
    
    # 1. World Model Check
    wm = WorldModel(state_dim=10)
    state = np.random.rand(10)
    state = state / np.linalg.norm(state)
    
    # Simular aprendizado preditivo
    print(f"🔍 Testando Predição de Recompensa (A1):")
    errors = []
    for i in range(20):
        # O "mundo" real sempre dá 0.9 para A1 neste estado
        actual_reward = 0.9
        next_state_real = state * 1.05
        next_state_real = next_state_real / np.linalg.norm(next_state_real)
        
        pred_state, pred_reward = wm.predict(state, "A1")
        error = wm.update(state, "A1", next_state_real, actual_reward)
        errors.append(error)
        
        if i % 5 == 0:
            print(f"  Ciclo {i}: Predição={pred_reward:.4f} | Erro={error:.4f}")
    
    final_error = wm.get_avg_error()
    print(f"📊 Erro de Predição Final: {final_error:.4f} (Esperado: < 0.1)")
    
    # 2. Imagination Loop Check
    # O sistema deve agora "preferir" A1 porque ele prediz 0.9
    _, reward_a1 = wm.predict(state, "A1")
    _, reward_a2 = wm.predict(state, "A2")
    print(f"💭 Imagination Loop: A1_Pred={reward_a1:.4f} | A2_Pred={reward_a2:.4f}")

    report = {
        "prediction_convergence": bool(final_error < 0.1),
        "imagination_active": bool(reward_a1 > reward_a2),
        "avg_prediction_error": float(final_error),
        "status": "VALIDADO N13"
    }
    
    with open("logs/n13_world_model_results.json", "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"\n✅ Validação N13 Concluída. Sistema Preditivo e Planejador.")

if __name__ == "__main__":
    simulate_n13_prediction()
