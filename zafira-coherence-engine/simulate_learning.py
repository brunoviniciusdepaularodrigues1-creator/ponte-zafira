import json
import time
import os
import random
from core.psi0_agent import Psi0Agent

# Mock de inputs para simulação de aprendizado
INPUTS = [
    {"input": "Caos quântico no vácuo UCS", "stage": "C", "coherence": 0.9},
    {"input": "Refinamento de parâmetros da Lagrangiana", "stage": "F", "coherence": 0.8},
    {"input": "Execução de rotina de limpeza de dados", "stage": "A", "coherence": 0.95},
    {"input": "Divergência na métrica de Friedmann", "stage": "C", "coherence": 0.7},
    {"input": "Ajuste fino de constantes cosmológicas", "stage": "F", "coherence": 0.85},
    {"input": "Sincronização de logs do sistema", "stage": "A", "coherence": 1.0}
]

def simulate_learning_cycles(num_cycles=10):
    print("="*60)
    print("🚀 SIMULANDO APRENDIZADO DO ZAFIRA COHERENCE ENGINE")
    print("="*60)
    
    agent = Psi0Agent()
    
    # Mock de resultados de executores
    results = {
        "v1": {"score": 0.8, "result": "EXECUTADO"},
        "v2": {"score": 0.9, "result": "EXECUTADO"},
        "llm": {"score": 0.95, "result": "LLM_PROCESSOU"}
    }

    for i in range(num_cycles):
        print(f"\n[Ciclo {i+1}]")
        
        # 1. Escolha de input
        top = random.choice(INPUTS)
        
        # 2. Seleção Probabilística
        chosen, probs = agent.select_strategy_probabilistic(top)
        print(f"Input: {top['input']} (Stage: {top['stage']})")
        print(f"Seleção: {chosen} (Probs: {['%.2f' % p for p in probs]})")
        
        # 3. Avaliação Interna
        res_data = results[chosen]
        internal_score = agent.internal_evaluate(chosen, res_data, top)
        
        # 4. Aprendizado
        agent.update_consequences(top["stage"], chosen, internal_score)
        print(f"Aprendizado: Score Interno {internal_score} registrado para {chosen} em {top['stage']}")
        
    print("\n" + "="*60)
    print("✅ APRENDIZADO CONCLUÍDO. Verifique core/agent_memory.json")
    print("="*60)

if __name__ == "__main__":
    simulate_learning_cycles()
