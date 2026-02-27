import numpy as np
import pandas as pd
from scipy.optimize import minimize
from run_ucs_model import UCSModel, load_observational_data
import matplotlib.pyplot as plt
from pathlib import Path

def objective_function(params, z_obs, H_obs, H_err):
    lambda_param, omega_m = params
    # Restrições físicas básicas
    if lambda_param < 0 or omega_m < 0.05 or omega_m > 0.5:
        return 1e10
    
    model = UCSModel(lambda_param=lambda_param, omega_m=omega_m, h0=67.4)
    chi2, _ = model.chi_squared(z_obs, H_obs, H_err)
    return chi2

def run_optimization():
    print("Iniciando Otimização de Nível Superior (Best Fit)...")
    data_path = Path(__file__).parent / "data" / "H_z_data.csv"
    z_obs, H_obs, H_err = load_observational_data(data_path)
    
    if z_obs is None:
        print("Erro: Dados não encontrados.")
        return

    # Chute inicial: lambda=0.1, omega_m=0.3
    initial_guess = [0.1, 0.3]
    
    # Minimização via Nelder-Mead para robustez em superfícies rugosas
    result = minimize(objective_function, initial_guess, args=(z_obs, H_obs, H_err), 
                      method='Nelder-Mead', tol=1e-6)
    
    best_lambda, best_omega_m = result.x
    min_chi2 = result.fun
    
    print(f"\nResultados da Otimização:")
    print(f"  Best-fit λ: {best_lambda:.6f}")
    print(f"  Best-fit Ω_m: {best_omega_m:.6f}")
    print(f"  Mínimo χ²: {min_chi2:.6f}")
    print(f"  χ²/dof: {min_chi2 / (len(z_obs)-2):.6f}")

    # Gerar Gráfico de Resíduos
    model_best = UCSModel(lambda_param=best_lambda, omega_m=best_omega_m, h0=67.4)
    _, H_model_best, _ = model_best.integrate_h_z(z_obs)
    
    # LCDM para comparação de resíduos (Omega_m=0.3 padrão)
    H_lcdm = 67.4 * np.sqrt(0.3 * (1 + z_obs)**3 + 0.7)
    
    residuos_ucs = H_obs - H_model_best
    residuos_lcdm = H_obs - H_lcdm
    
    plt.figure(figsize=(10, 6))
    plt.axhline(0, color='black', linestyle='--', alpha=0.5)
    plt.errorbar(z_obs, residuos_ucs, yerr=H_err, fmt='ro', label='Resíduos UCS (Best Fit)')
    plt.errorbar(z_obs, residuos_lcdm, yerr=H_err, fmt='bo', alpha=0.5, label='Resíduos LCDM')
    
    plt.xlabel('Redshift z')
    plt.ylabel('H_obs - H_model')
    plt.title('Análise de Resíduos: Precisão da Convergência')
    plt.legend()
    plt.grid(True, alpha=0.2)
    plt.savefig('analise_residuos.png', dpi=300)
    print("Gráfico de resíduos salvo em analise_residuos.png")

    return best_lambda, best_omega_m, min_chi2

if __name__ == "__main__":
    run_optimization()
