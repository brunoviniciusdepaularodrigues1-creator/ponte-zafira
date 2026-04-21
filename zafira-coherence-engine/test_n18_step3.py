import os
import sys
import json

# Adicionar a raiz do projeto ao sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '.')))

from core.psi0_agent import Psi0Agent

def run_step3_test():
    print("🚀 Iniciando Teste de Autorreferência - N18 Passo 3")
    agent = Psi0Agent(interval=0)
    
    # Simular uma tarefa que resultará em baixa recompensa (Pobre Decisão)
    print("\n--- Teste 1: Pobre Decisão (Simulada) ---")
    task_input = "Resolva o sistema impossível: x=1, x=2."
    chosen_action = "A1"
    internal_score = 0.1 # Simula falha catastrófica
    
    # Atualizar estado interno e disparar flag
    agent.meta.state.update(task_input, chosen_action, internal_score)
    if internal_score < 0.3:
        agent.meta.flag_poor_decision(task_input)
        
    print(f"  Estado Interno Atual: {agent.meta.state.__dict__}")
    
    # Simular uma tarefa de alta recompensa (Boa Decisão)
    print("\n--- Teste 2: Boa Decisão (Simulada) ---")
    task_input_2 = "2+2"
    chosen_action_2 = "A2"
    internal_score_2 = 0.9
    
    agent.meta.state.update(task_input_2, chosen_action_2, internal_score_2)
    if internal_score_2 < 0.3:
        agent.meta.flag_poor_decision(task_input_2)
    else:
        print(f"  Decisão aceitável. Nenhuma flag disparada.")
        
    print(f"  Estado Interno Atual: {agent.meta.state.__dict__}")
    
    print("\n✅ Teste de Autorreferência concluído.")

if __name__ == "__main__":
    run_step3_test()
