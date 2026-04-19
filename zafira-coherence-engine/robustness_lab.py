import random
import numpy as np
import pandas as pd

def simulate_strategy_a(initial_capital, cycles, p_crash, crash_impact=0.95, normal_return=0.10):
    capital = initial_capital
    for _ in range(cycles):
        if capital < 1.0: return 0
        investment = capital * 0.75
        if random.random() < p_crash:
            capital -= investment * crash_impact
        else:
            capital += investment * normal_return
    return max(0, capital)

def simulate_strategy_b(initial_capital, cycles, p_crash, threshold_sigma=1.5, crash_impact=0.95, normal_return=0.10):
    capital = initial_capital
    volatilities = [0.05] * 5
    for _ in range(cycles):
        if capital < 1.0: return 0
        current_sigma = np.std(volatilities[-5:])
        avg_sigma = np.mean(volatilities[-5:])
        
        if current_sigma > threshold_sigma * avg_sigma:
            investment = capital * 0.05
        else:
            investment = capital * 0.25
            
        if random.random() < p_crash:
            capital -= investment * crash_impact
            volatilities.append(0.8)
        else:
            capital += investment * normal_return
            volatilities.append(0.05)
    return max(0, capital)

def run_robustness_test(iterations=10000):
    scenarios = [
        {"name": "Otimista (P_crash=0.05)", "p_crash": 0.05, "impact": 0.80, "ret": 0.15},
        {"name": "Base (P_crash=0.15)", "p_crash": 0.15, "impact": 0.95, "ret": 0.10},
        {"name": "Pessimista (P_crash=0.30)", "p_crash": 0.30, "impact": 0.98, "ret": 0.05},
    ]
    
    thresholds = [1.2, 1.5, 2.0]
    
    print(f"--- LABORATÓRIO DE ROBUSTEZ (Iterações: {iterations}) ---")
    
    for scenario in scenarios:
        print(f"\nCenário: {scenario['name']}")
        
        # Testar Estratégia A
        results_a = [simulate_strategy_a(400, 50, scenario['p_crash'], scenario['impact'], scenario['ret']) for _ in range(iterations)]
        ruin_a = sum(1 for r in results_a if r < 1.0) / iterations
        print(f"  Estratégia A: Saldo Médio R$ {np.mean(results_a):.2f} | Ruína {ruin_a*100:.1f}%")
        
        # Testar Estratégia B com diferentes Thresholds
        for t in thresholds:
            results_b = [simulate_strategy_b(400, 50, scenario['p_crash'], t, scenario['impact'], scenario['ret']) for _ in range(iterations)]
            ruin_b = sum(1 for r in results_b if r < 1.0) / iterations
            print(f"  Estratégia B ({t}σ): Saldo Médio R$ {np.mean(results_b):.2f} | Ruína {ruin_b*100:.1f}%")

if __name__ == "__main__":
    run_robustness_test()
