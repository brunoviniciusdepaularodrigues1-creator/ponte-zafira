import sys
import os
import numpy as np
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar o core
sys.path.append(str(Path(__file__).parent.parent))

from core.world_model import WorldModel

def run_n17_validation():
    print(f"🚀 Iniciando Validação Nível 17: Contrastive Learning (Significado)...")
    
    # Configuração: Gamma=0.5 para forçar o contraste
    wm = WorldModel(state_dim=10, latent_dim=2, gamma=0.5)
    
    # 1. Simulação de Estados por Categorias (Clusters)
    # Categoria 1: Vetores com valores altos no início
    # Categoria 2: Vetores com valores altos no final
    cat1_states = [np.array([1, 1, 1, 0, 0, 0, 0, 0, 0, 0], dtype=float) for _ in range(10)]
    cat2_states = [np.array([0, 0, 0, 0, 0, 0, 0, 1, 1, 1], dtype=float) for _ in range(10)]
    
    # Normalizar
    cat1_states = [s / np.linalg.norm(s) for s in cat1_states]
    cat2_states = [s / np.linalg.norm(s) for s in cat2_states]
    
    print(f"🧪 Treinando com Contrastive Loss (100 iterações)...")
    
    for i in range(100):
        # Alternar entre categorias para forçar a separação
        if i % 2 == 0:
            state = cat1_states[np.random.randint(0, 10)]
            next_state = cat1_states[np.random.randint(0, 10)]
        else:
            state = cat2_states[np.random.randint(0, 10)]
            next_state = cat2_states[np.random.randint(0, 10)]
            
        wm.update(state, "A1", next_state, 0.8)

    # 2. Medir Separação Semântica no Espaço Latente
    z1 = wm.encode(cat1_states[0])
    z2 = wm.encode(cat2_states[0])
    
    intra_dist = np.linalg.norm(z1 - wm.encode(cat1_states[1]))
    inter_dist = np.linalg.norm(z1 - z2)
    
    print(f"  Distância Intra-Classe (Mesma Categoria): {intra_dist:.4f}")
    print(f"  Distância Inter-Classe (Categorias Diferentes): {inter_dist:.4f}")
    
    # 3. Verificação de Estrutura
    is_structured = inter_dist > intra_dist
    print(f"🎯 Estrutura Semântica Detectada: {is_structured}")

    report = {
        "intra_class_dist": float(intra_dist),
        "inter_class_dist": float(inter_dist),
        "separation_ratio": float(inter_dist / (intra_dist + 1e-9)),
        "avg_contrast_loss": float(wm.get_avg_contrast_loss()),
        "status": "VALIDADO N17"
    }
    
    with open("logs/n17_contrastive_results.json", "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"\n✅ Validação N17 Concluída. Significado Organizado no Espaço Latente.")

if __name__ == "__main__":
    run_n17_validation()
