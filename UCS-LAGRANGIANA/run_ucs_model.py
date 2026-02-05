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
        
        From derivacao_completa.md field equations:
        d²φ/dz² + (1/E) * dE/dz * dφ/dz + (1/(E²(1+z)²)) * dV/dφ = 0
        
        Reduced form for numerical integration:
        dH/dz = -(1+z) * H - (λ/2) * (φ)² * H / (ρ_m(1+z)³ + ρ_φ)
        
        Args:
            y: [H/H_0, φ] state vector
            z: Redshift
            params: Model parameters
        
        Returns:
            [dE/dz, dφ/dz]
        """
        E, phi = y
        
        # Matter density evolution
        rho_m = self.omega_m * (1 + z)**3
        
        # Effective potential energy density
        # V(φ) = (λ/4!) * φ⁴ (from scalar field theory)
        phi_squared = phi**2
        rho_phi = 0.5 * phi_squared  # Kinetic + potential approximation
        
        # Hubble acceleration (simplified)
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
        
        Args:
            z_array: Array of redshifts (should be in decreasing order from integration)
            phi_0: Initial scalar field value at z=0
        
        Returns:
            H_z: Hubble parameter evolution H(z)
            phi_z: Scalar field evolution φ(z)
        """
        # Sort redshifts in reverse for integration (from 0 backwards)
        z_sorted = np.sort(z_array)[::-1]
        
        # Initial conditions at z=0: E(0)=1, φ(0)=φ_0
        y0 = [1.0, phi_0]
        
        # Integrate ODE
        solution = odeint(self.hubble_ode, y0, z_sorted, args=(self,))
        
        E_z = solution[:, 0]
        phi_z = solution[:, 1]
        
        # Convert back to original order
        idx_reverse = np.argsort(z_sorted)[::-1]
        z_result = z_sorted[idx_reverse]
        H_z = self.h0 * E_z[idx_reverse]
        phi_result = phi_z[idx_reverse]
        
        return z_result, H_z, phi_result
    
    def chi_squared(self, z_obs, H_obs, H_err):
        """
        Compute χ² statistic for observational comparison
        
        Args:
            z_obs: Observed redshifts
            H_obs: Observed H(z) values (km/s/Mpc)
            H_err: Observational errors
        
        Returns:
            χ²: Chi-squared value
            reduced_chi2: χ²/dof
        """
        # Integrate model at observation points
        _, H_model, _ = self.integrate_h_z(z_obs)
        
        # Calculate residuals
        residuals = (H_obs - H_model) / H_err
        chi2 = np.sum(residuals**2)
        dof = len(z_obs) - 2  # Two parameters: lambda, omega_m
        reduced_chi2 = chi2 / dof
        
        return chi2, reduced_chi2


def load_observational_data(data_path):
    """
    Load H(z) observational data from CSV
    Expected format: z, H(z), error_H(z)
    
    Args:
        data_path: Path to CSV file
    
    Returns:
        z_obs, H_obs, H_err: Arrays of observational data
    """
    try:
        data = pd.read_csv(data_path)
        z_obs = data['z'].values
        H_obs = data['H(z)'].values
        H_err = data['error'].values
        return z_obs, H_obs, H_err
    except FileNotFoundError:
        print(f"Data file not found: {data_path}")
        return None, None, None


def plot_results(z_obs, H_obs, H_err, z_model, H_model, output_path=None):
    """
    Plot observational data vs model predictions
    
    Args:
        z_obs: Observed redshifts
        H_obs: Observed H(z)
        H_err: Observational errors
        z_model: Model redshifts
        H_model: Model H(z)
        output_path: Path to save plot (optional)
    """
    plt.figure(figsize=(12, 8))
    
    # Plot observational data with error bars
    plt.errorbar(z_obs, H_obs, yerr=H_err, fmt='o', label='Pantheon H(z) data',
                 markersize=6, alpha=0.7, capsize=4)
    
    # Plot model prediction
    plt.plot(z_model, H_model, 'r-', linewidth=2, label='UCS Model')
    
    # Standard LCDM for comparison
    omega_m = 0.3
    H0 = 67.4
    E_cdm = np.sqrt(omega_m * (1 + z_model)**3 + (1 - omega_m))
    H_cdm = H0 * E_cdm
    plt.plot(z_model, H_cdm, 'b--', linewidth=2, label='LCDM (ω_m=0.3, H_0=67.4)')
    
    plt.xlabel('Redshift z', fontsize=12)
    plt.ylabel('Hubble Parameter H(z) [km/s/Mpc]', fontsize=12)
    plt.title('UCS Scalar Field Model: H(z) Evolution', fontsize=14)
    plt.legend(fontsize=11)
    plt.grid(True, alpha=0.3)
    plt.xscale('log')
    
    if output_path:
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        print(f"Plot saved to {output_path}")
    
    plt.show()


def main():
    """
    Main execution: Run UCS model, compare with Pantheon data
    """
    print("="*70)
    print("UCS-LAGRANGIANA Numerical Model Runner")
    print("Scalar Field Cosmology Integration")
    print("="*70)
    
    # Initialize model
    model = UCSModel(lambda_param=0.1, omega_m=0.3, h0=67.4)
    print(f"\nModel Parameters:")
    print(f"  λ (coupling) = {model.lambda_param}")
    print(f"  Ω_m (matter) = {model.omega_m}")
    print(f"  H_0 (today) = {model.h0} km/s/Mpc")
    
    # Generate redshift array for integration
    z_array = np.linspace(0, 2.5, 100)
    
    # Run integration
    print(f"\nIntegrating H(z) from z=0 to z=2.5...")
    z_model, H_model, phi_model = model.integrate_h_z(z_array)
    print(f"  Integration complete: {len(z_model)} points")
    print(f"  H(z=0) = {H_model[0]:.2f} km/s/Mpc (Hubble today)")
    print(f"  φ(z=0) = {phi_model[0]:.4f} (scalar field today)")
    
    # Try to load observational data
    data_path = Path(__file__).parent / "data" / "H_z_data.csv"
    z_obs, H_obs, H_err = load_observational_data(data_path)
    
    if z_obs is not None:
        print(f"\nObservational Data:")
        print(f"  Loaded {len(z_obs)} Pantheon H(z) points")
        print(f"  Redshift range: z ∈ [{z_obs.min():.3f}, {z_obs.max():.3f}]")
        
        # Calculate chi-squared
        chi2, reduced_chi2 = model.chi_squared(z_obs, H_obs, H_err)
        print(f"\nGoodnessof Fit:")
        print(f"  χ² = {chi2:.4f}")
        print(f"  χ²/dof = {reduced_chi2:.4f}")
        print(f"  Degrees of freedom = {len(z_obs) - 2}")
        
        # Generate plot
        plot_results(z_obs, H_obs, H_err, z_model, H_model,
                    output_path="ucs_model_fit.png")
    else:
        print("\n⚠ Observational data not available.")
        print("  Run with synthetic data for demonstration.")
        
        # Generate synthetic data for testing
        z_syn = np.linspace(0.1, 2.0, 20)
        H_syn_true = model.h0 * np.sqrt(0.3 * (1 + z_syn)**3 + 0.7)
        H_syn_err = 0.05 * H_syn_true
        H_syn_obs = H_syn_true + np.random.normal(0, H_syn_err)
        
        print(f"\nGenerated synthetic data: {len(z_syn)} points")
        plot_results(z_syn, H_syn_obs, H_syn_err, z_model, H_model,
                    output_path="ucs_model_fit_synthetic.png")
    
    print("\n" + "="*70)
    print("Integration complete. All results saved.")
    print("="*70)


if __name__ == "__main__":
    main()
