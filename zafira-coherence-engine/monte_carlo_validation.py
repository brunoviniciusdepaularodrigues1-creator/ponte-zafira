import random
import numpy as np

def simulate_strategy_a(initial_capital, cycles, p_crash):
    """Estratégia A: Alocação Fixa (75%) | Sem Gatilho de Saída"""
    capital = initial_capital
    for _ in range(cycles):
        if capital <= 0: break
        
        investment = capital * 0.75
        if random.random() < p_crash:
            # Crash: Perda de 95% do investimento (Agressivo)
            capital -= investment * 0.95
        else:
            # Normal: Ganho de 10% do investimento
            capital += investment * 0.10
    return max(0, capital)

def simulate_strategy_b(initial_capital, cycles, p_crash, threshold_sigma=1.5):
    """Estratégia B (UCS): Alocação Fracionada (25%) | Gatilho de Saída (1.5x sigma)"""
    capital = initial_capital
    volatilities = [0.05] * 5 
    
    for _ in range(cycles):
        if capital <= 0: break
        
        current_sigma = np.std(volatilities[-5:])
        avg_sigma = np.mean(volatilities[-5:])
        
        # Gatilho de Saída
        if current_sigma > threshold_sigma * avg_sigma:
            investment = capital * 0.05 # Redução drástica
        else:
            investment = capital * 0.25
            
        if random.random() < p_crash:
            capital -= investment * 0.95
            volatilities.append(0.8) # Pânico no mercado
        else:
            capital += investment * 0.10
            volatilities.append(0.05)
            
    return max(0, capital)

def run_monte_carlo(iterations=1000, cycles=100, p_crash=0.15):
    results_a = []
    results_b = []
    ruin_a = 0
    ruin_b = 0
    
    for _ in range(iterations):
        res_a = simulate_strategy_a(400, cycles, p_crash)
        res_b = simulate_strategy_b(400, cycles, p_crash)
        
        results_a.append(res_a)
        results_b.append(res_b)
        
        if res_a < 1.0: ruin_a += 1 # Considera ruína se capital < 1
        if res_b < 1.0: ruin_b += 1
        
    print(f"--- STRESS TEST MONTE CARLO (Iterações: {iterations}, Ciclos: {cycles}, P_Crash: {p_crash}) ---")
    print(f"Estratégia A (Frágil):")
    print(f"  Saldo Médio: R$ {np.mean(results_a):.2f}")
    print(f"  Probabilidade de Ruína: {(ruin_a/iterations)*100:.1f}%")
    print(f"Estratégia B (Antifrágil):")
    print(f"  Saldo Médio: R$ {np.mean(results_b):.2f}")
    print(f"  Probabilidade de Ruína: {(ruin_b/iterations)*100:.1f}%")
    print(f"------------------------------------------------------------------")

if __name__ == "__main__":
    run_monte_carlo()
