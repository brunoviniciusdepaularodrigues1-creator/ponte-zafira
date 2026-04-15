import json
import time
import os
import random
import subprocess
from datetime import datetime, timedelta

# Configurações
BASE_DIR = "/home/ubuntu/psi0-budget-system"
BRIDGE_FILE = os.path.join(BASE_DIR, "bridge_interface.json")
ORCHESTRATOR_SCRIPT = os.path.join(BASE_DIR, "ponte_zafira/orchestrator.py")

# Mock de inputs para simulação
INPUTS = [
    {"input": "Análise de flutuações quânticas no vácuo UCS", "stage": "C", "coherence": 0.92},
    {"input": "Otimização de parâmetros da Lagrangiana", "stage": "F", "coherence": 0.88},
    {"input": "Execução de rotina de limpeza de dados H(z)", "stage": "A", "coherence": 0.95},
    {"input": "Divergência detectada na métrica de Friedmann", "stage": "C", "coherence": 0.75},
    {"input": "Refinamento de axiomas da PCU", "stage": "F", "coherence": 0.98},
    {"input": "Sincronização de logs do sistema", "stage": "A", "coherence": 1.0},
    {"input": "Exploração de novas dimensões compactadas", "stage": "C", "coherence": 0.65},
    {"input": "Ajuste fino de constantes cosmológicas", "stage": "F", "coherence": 0.82}
]

EXECUTORS = ["v1", "v2", "llm"]

def simulate_cycle(cycle_num, last_stage=None):
    print(f"\n--- Simulando Ciclo {cycle_num + 1} ---")
    
    # 1. ψ₀ decide (Simulado com lógica de transição progressiva)
    if last_stage == "C":
        choice = next(i for i in INPUTS if i["stage"] == "F")
        print(f"ψ₀ forçou transição progressiva: C -> F")
    else:
        choice = random.choice(INPUTS)
    
    timestamp = (datetime.now() - timedelta(minutes=(10 - cycle_num) * 5)).isoformat()
    
    bridge_data = {
        "agent": "psi0",
        "timestamp": timestamp,
        "generation": cycle_num,
        "best_executor": random.choice(EXECUTORS),
        "feedback_applied": round(random.uniform(0.7, 0.99), 2),
        "best_decision": choice,
        "network_status": [
            {"executor": "v1", "score": 0.85},
            {"executor": "v2", "score": 0.90},
            {"executor": "llm", "score": 0.95}
        ]
    }
    
    with open(BRIDGE_FILE, "w") as f:
        json.dump(bridge_data, f, indent=2, ensure_ascii=False)
    
    print(f"ψ₀ enviou decisão: {choice['input']} (Stage: {choice['stage']})")
    
    # 2. Orquestrador processa (Execução Real do script modificado)
    original_cwd = os.getcwd()
    os.chdir(os.path.join(BASE_DIR, "ponte_zafira"))
    
    try:
        # Criar arquivos de resultado mockados para os executores
        os.makedirs("../executor_agent", exist_ok=True)
        os.makedirs("../executor_agent_v2", exist_ok=True)
        os.makedirs("../executor_llm", exist_ok=True)
        
        with open("../executor_agent/execution_result.json", "w") as f:
            json.dump({"result": "EXECUTADO", "score": 1.0}, f)
        with open("../executor_agent_v2/execution_result_v2.json", "w") as f:
            json.dump({"result": "EXECUTADO", "score": 1.0}, f)
        with open("../executor_llm/execution_result_llm.json", "w") as f:
            json.dump({"result": "LLM_PROCESSOU", "score": 0.9}, f)

        proc = subprocess.Popen(["python3", "orchestrator.py"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        time.sleep(2)
        proc.terminate()
        print("Orquestrador processou o ciclo.")
    finally:
        os.chdir(original_cwd)
    
    return choice["stage"]

if __name__ == "__main__":
    # Limpar histórico anterior para nova análise de otimização
    LOG_FILE = os.path.join(BASE_DIR, "logs/system_history.json")
    if os.path.exists(LOG_FILE):
        os.remove(LOG_FILE)
        print("Histórico anterior removido para nova análise de otimização.")

    print("Iniciando simulação de 10 ciclos otimizados...")
    last_stage = None
    for i in range(10):
        last_stage = simulate_cycle(i, last_stage)
    print("\nSimulação concluída. Verifique logs/system_history.json")
