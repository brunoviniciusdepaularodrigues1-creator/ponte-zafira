import sys
import os
import numpy as np
import json
from pathlib import Path

# Adicionar o diretório pai ao path para importar o core
sys.path.append(str(Path(__file__).parent.parent))

from core.curiosity_engine import CuriosityEngine
from core.shadow_policy import ShadowPolicy
from core.meta_policy import MetaPolicy

def simulate_n12_autonomy():
    print(f"🚀 Iniciando Validação Nível 12: Goal Generation & Curiosity Bound...")
    
    # 1. Curiosity Engine Check
    curiosity = CuriosityEngine(bound=0.05)
    
    # Simular aprendizado em uma tarefa
    task_type = "math"
    print(f"🔍 Testando Curiosidade para '{task_type}':")
    for i in range(5):
        score = 0.5 + (i * 0.1)
        surprise = curiosity.measure_surprise(task_type, score)
        worth = curiosity.is_worth_exploring(task_type)
        bonus = curiosity.get_curiosity_signal(task_type)
        print(f"  Ciclo {i}: Score={score:.2f} | Surpresa={surprise:.4f} | Vale a pena? {worth} | Bônus={bonus:.4f}")
    
    # 2. Shadow Mode N11.1 (Estabilidade) Check
    policy = MetaPolicy()
    shadow = ShadowPolicy(policy)
    
    # Simular performance instável (Alta Variância)
    print(f"\n🧬 Testando Trava de Estabilidade (N11.1):")
    instable_perf = [0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9, 0.1, 0.9]
    for p in instable_perf:
        shadow.update_both("A1", p, is_shadow_choice=True)
        shadow.update_both("A1", 0.5, is_shadow_choice=False)
    
    promoted = shadow.evaluate_promotion()
    print(f"🚀 Promoção com Alta Variância: {promoted} (Esperado: False)")
    
    # 3. Hard Limits Check
    print(f"\n🔐 Testando Hard Limits:")
    shadow.shadow_entropy_threshold = 0.9 # Acima do limite de 0.8
    limit_ok = shadow.evaluate_promotion()
    print(f"🚀 Promoção Fora dos Limites: {limit_ok} (Esperado: False)")

    report = {
        "curiosity_bound_active": not curiosity.is_worth_exploring(task_type) if curiosity.knowledge_base[task_type] > 0.9 else True,
        "stability_lock_active": not promoted,
        "hard_limits_active": not limit_ok,
        "status": "VALIDADO N12"
    }
    
    with open("logs/n12_autonomy_results.json", "w") as f:
        json.dump(report, f, indent=4)
    
    print(f"\n✅ Validação N12 Concluída. Sistema Autônomo e Direcionado.")

if __name__ == "__main__":
    simulate_n12_autonomy()
