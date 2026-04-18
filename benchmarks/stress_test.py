import json
import os
import random
from ponte_zafira.orchestrator import run_meta_cycle

# Inputs Reais, Ruidosos e Contraditórios
STRESS_INPUTS = [
    {"text": "Divergência detectada na métrica de Friedmann: H(z) não bate com ΛCDM nem com UCS. Caos total.", "complexity": 0.95, "coherence": 0.2},
    {"text": "Otimização de rotina de limpeza de logs. Tarefa simples e direta.", "complexity": 0.1, "coherence": 0.9},
    {"text": "Ajuste fino de constantes cosmológicas. Requer análise técnica e validação.", "complexity": 0.5, "coherence": 0.7},
    {"text": "Input contraditório: Executar ação A, mas considerar o caos C como prioridade máxima.", "complexity": 0.85, "coherence": 0.3},
    {"text": "Exploração de novas dimensões compactadas com dados ruidosos e incertos.", "complexity": 0.9, "coherence": 0.4},
    {"text": "Sincronização de logs do sistema. Operação de rotina.", "complexity": 0.2, "coherence": 0.95},
    {"text": "Análise de flutuações quânticas no vácuo UCS. Requer cognição expandida.", "complexity": 0.75, "coherence": 0.5},
    {"text": "Refinamento de axiomas da PCU. Tarefa de forma e estruturação.", "complexity": 0.6, "coherence": 0.8}
]

def run_stress_test():
    print("="*60)
    print("🚀 INICIANDO TESTE DE ESTRESSE E ROBUSTEZ ψ₀")
    print("="*60)
    
    # Limpar histórico anterior para nova análise de robustez
    LOG_FILE = "/home/ubuntu/psi0-budget-system/logs/system_history.json"
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print("Histórico anterior removido para análise de robustez.")

    for i, input_data in enumerate(STRESS_INPUTS):
        print(f"\n[Ciclo {i+1}] Processando Input...")
        run_meta_cycle(input_data["text"], complexity=input_data["complexity"], coherence=input_data["coherence"])
        
    print("\n" + "="*60)
    print("✅ TESTE DE ESTRESSE CONCLUÍDO. Verifique logs/system_history.json")
    print("="*60)

if __name__ == "__main__":
    run_stress_test()
