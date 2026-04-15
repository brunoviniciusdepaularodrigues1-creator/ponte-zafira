import json
import time
import os
import datetime
import subprocess

# Configurações de Caminhos (Atualizado para Zafira Coherence Engine)
BASE_DIR = "/home/ubuntu/zafira-coherence-engine"
LOG_FILE = os.path.join(BASE_DIR, "logs/system_history.json")
ORCHESTRATOR_LOG = os.path.join(BASE_DIR, "ponte_zafira/orchestrator_log.json")

# Nós ψ₀ Disponíveis
NODES = {
    "psi0_node_1": {"dir": os.path.join(BASE_DIR, "psi0_node_1"), "profile": "Conservador"},
    "psi0_node_2": {"dir": os.path.join(BASE_DIR, "psi0_node_2"), "profile": "Exploratório"},
    "psi0_node_3": {"dir": os.path.join(BASE_DIR, "psi0_node_3"), "profile": "Analítico"}
}

def log_event(data):
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    history = []
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, "r") as f:
                history = json.load(f)
        except: pass
    history.append(data)
    with open(LOG_FILE, "w") as f:
        json.dump(history, f, indent=2, ensure_ascii=False)

def select_node(input_data):
    """Meta-Orquestração com Detecção de Incerteza."""
    complexity = input_data.get("complexity", 0.5)
    coherence = input_data.get("coherence", 0.5)
    uncertainty = 1.0 - coherence
    
    if uncertainty > 0.7:
        return "psi0_node_3", "INCERTEZA CRÍTICA: Ativando Modo de Degradação (Nó Analítico)"
    
    if complexity > 0.8:
        return "psi0_node_2", "Alta complexidade detectada: Usando Nó Exploratório"
    elif complexity < 0.3:
        return "psi0_node_1", "Baixa complexidade detectada: Usando Nó Conservador"
    else:
        return "psi0_node_3", "Complexidade média detectada: Usando Nó Analítico"

def decide_executor(node_decision, input_data):
    """Orquestração de Execução com Modo de Degradação."""
    stage = node_decision["stage"]
    coherence = node_decision["coherence"]
    uncertainty = 1.0 - coherence
    
    if uncertainty > 0.6:
        return "llm", "MODO DEGRADAÇÃO: Incerteza alta, solicitando reforço cognitivo (LLM)"
    
    if stage == "C":
        return "v2", "Priorizando V2 para estruturação do Caos"
    elif stage == "F":
        return "v2", "Executando refinamento técnico com V2"
    elif coherence < 0.4:
        return "llm", "Baixa coerência detectada: Fallback para LLM"
    else:
        return "v1", "Executando ação técnica com V1"

def run_meta_cycle(input_text, complexity=0.5, coherence=0.5):
    print(f"\n--- Ciclo de Meta-Orquestração: {input_text[:30]}... ---")
    
    # 1. Seleção de Nó
    input_data = {"text": input_text, "complexity": complexity, "coherence": coherence}
    node_id, node_reason = select_node(input_data)
    print(f"Ponte selecionou: {node_id} ({NODES[node_id]['profile']}) | Motivo: {node_reason}")
    
    # 2. Execução do Nó (Simulada via script)
    node_dir = NODES[node_id]["dir"]
    # Aqui chamaríamos o runner real, mas para simulação vamos usar a lógica interna
    # Import dinâmico para evitar problemas de path
    import sys
    sys.path.append(os.path.join(BASE_DIR))
    from core.psi0_node_runner import Psi0Node
    node = Psi0Node(node_dir)
    decision = node.process_input(input_data)
    
    # 3. Seleção de Executor com Modo de Degradação
    executor, exec_reason = decide_executor(decision["best_decision"], input_data)
    print(f"Ponte selecionou executor: {executor} | Motivo: {exec_reason}")
    
    # 4. Registro de Observabilidade com Análise de Falha
    failure_type = "none"
    if coherence < 0.3: failure_type = "ambiguity"
    if complexity > 0.9 and coherence < 0.5: failure_type = "overload"
    if "contraditório" in input_text.lower(): failure_type = "contradiction"

    log_event({
        "timestamp": datetime.datetime.now().isoformat(),
        "input": input_text,
        "complexity": complexity,
        "node": node_id,
        "profile": NODES[node_id]["profile"],
        "stage": decision["best_decision"]["stage"],
        "executor": executor,
        "coherence": coherence,
        "uncertainty": 1.0 - coherence,
        "failure_type": failure_type,
        "global_score": 0.9 if executor != "llm" else 0.85,
        "reason": f"{node_reason} -> {exec_reason}"
    })

if __name__ == "__main__":
    # Teste rápido de meta-orquestração
    run_meta_cycle("Teste de Meta-Orquestração", complexity=0.9)
    run_meta_cycle("Teste de Meta-Orquestração", complexity=0.1)
