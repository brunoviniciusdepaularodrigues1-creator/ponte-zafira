#!/usr/bin/env python3
"""
run_ucs_model.py
Numerical integration of UCS-LAGRANGIANA scalar field model
Integrates H(z) equation using Runge-Kutta 4th order method
Compares with observational H(z) data from Pantheon survey
"""

import numpy as np
import pandas as pd
from scipy.integrate import odeint
import matplotlib.pyplot as plt
from pathlib import Path


class UCSModel:
    """
    UCS Scalar Field Cosmology Model
    Implements numerical integration of H(z) from field equations
    """
    
    def __init__(self, lambda_param=0.1, omega_m=0.3, h0=67.4):
        """
        Initialize model parameters
        
        Args:
            lambda_param: Scalar field coupling strength (dimensionless)
            omega_m: Matter density parameter Ω_m
            h0: Hubble parameter today H_0 (km/s/Mpc)
        """
        self.lambda_param = lambda_param
        self.omega_m = omega_m
        self.h0 = h0
        self.omega_lambda = 1.0 - omega_m  # Flat universe
        
    def hubble_ode(self, y, z, params):
        """
        ODE for Hubble parameter evolution
        dy/dz = dE/dz where E = H(z)/H_0
        """
        E, phi = y
        
        # Matter density evolution
        rho_m = self.omega_m * (1 + z)**3
        
        # Effective potential energy density
        # V(φ) = (λ/4!) * φ⁴ (from scalar field theory)
        phi_squared = phi**2
        rho_phi = 0.5 * phi_squared  # Kinetic + potential approximation
        
        # Hubble acceleration
        if E > 0.01:  # Avoid division by zero
            dE_dz = -3 * (1 + z)**(-2) * (rho_m + rho_phi) / (2 * E)
        else:
            dE_dz = -3 * (1 + z)**(-2) * rho_m / 2
        
        # Scalar field evolution
        # dφ/dz from field equation
        d_phi_dz = -self.lambda_param * phi / ((1 + z) * E)
        
        return [dE_dz, d_phi_dz]
    
    def integrate_h_z(self, z_array, phi_0=0.5):
        """
        Integrate H(z) from z=0 (today) backwards to z_max
        """
        z_sorted = np.sort(z_array)[::-1]
        y0 = [1.0, phi_0]
        solution = odeint(self.hubble_ode, y0, z_sorted, args=(self,))
        E_z = solution[:, 0]
        phi_z = solution[:, 1]
        idx_reverse = np.argsort(z_sorted)[::-1]
        H_z = self.h0 * E_z[idx_reverse]
        phi_result = phi_z[idx_reverse]
        return z_array, H_z, phi_result
    
    def chi_squared(self, z_obs, H_obs, H_err):
        """
        Compute χ² statistic for observational comparison
        """
        _, H_model, _ = self.integrate_h_z(z_obs)
        residuals = (H_obs - H_model) / H_err
        chi2 = np.sum(residuals**2)
        dof = len(z_obs) - 2
        reduced_chi2 = chi2 / dof
        return chi2, reduced_chi2


def load_observational_data(data_path):
    """
    Load H(z) observational data from CSV
    """
    try:
        data = pd.read_csv(data_path)
        z_obs = data['z'].values
        H_obs = data['H_obs_km_s_Mpc'].values
        H_err = data['sigma_H'].values
        return z_obs, H_obs, H_err
    except Exception as e:
        print(f"Error loading data: {e}")
        return None, None, None


def plot_results(z_obs, H_obs, H_err, z_model, H_model, H_zero, output_path=None):
    """
    Plot observational data vs model predictions
    """
    plt.figure(figsize=(12, 8))
    
    # Plot observational data
    plt.errorbar(z_obs, H_obs, yerr=H_err, fmt='o', color='black', label='Pantheon H(z) data',
                 markersize=6, alpha=0.7, capsize=4)
    
    # Plot UCS Model
    plt.plot(z_model, H_model, 'r-', linewidth=2, label='UCS Model (λ=0.1)')
    
    # Plot Zero Field Model
    plt.plot(z_model, H_zero, 'g--', linewidth=2, label='Zero Field (λ=0.0)')
    
    # Standard LCDM for comparison
    omega_m = 0.3
    H0 = 67.4
    E_cdm = np.sqrt(omega_m * (1 + z_model)**3 + (1 - omega_m))
    H_cdm = H0 * E_cdm
    plt.plot(z_model, H_cdm, 'b:', linewidth=2, label='LCDM (Standard)')
    
    plt.xlabel('Redshift z', fontsize=12)
    plt.ylabel('Hubble Parameter H(z) [km/s/Mpc]', fontsize=12)
    plt.title('Cosmological Comparison: UCS vs Zero Field vs LCDM', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    plt.close()


def main():
    print("="*70)
    print("UCS-LAGRANGIANA Comparison Runner (Including Zero Field)")
    print("="*70)
    
    # Models
    model_ucs = UCSModel(lambda_param=0.1, omega_m=0.3, h0=67.4)
    model_zero = UCSModel(lambda_param=0.0, omega_m=0.3, h0=67.4)
    
    z_array = np.linspace(0, 2.5, 100)
    
    # Run integrations
    _, H_ucs, _ = model_ucs.integrate_h_z(z_array)
    _, H_zero, _ = model_zero.integrate_h_z(z_array)
    
    # Load data
    data_path = Path(__file__).parent / "data" / "H_z_data.csv"
    z_obs, H_obs, H_err = load_observational_data(data_path)
    
    if z_obs is not None:
        chi2_ucs, _ = model_ucs.chi_squared(z_obs, H_obs, H_err)
        chi2_zero, _ = model_zero.chi_squared(z_obs, H_obs, H_err)
        
        print(f"Goodness of Fit (Chi-squared):")
        print(f"  UCS (λ=0.1): {chi2_ucs:.4f}")
        print(f"  Zero Field:   {chi2_zero:.4f}")
        
        plot_results(z_obs, H_obs, H_err, z_array, H_ucs, H_zero,
                    output_path="comparison_results.png")
    
    print("\nIntegration complete. Results saved.")


if __name__ == "__main__":
    main()
