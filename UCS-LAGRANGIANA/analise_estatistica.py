#!/usr/bin/env python3
"""
analise_estatistica.py
Statistical validation and hypothesis testing for UCS-LAGRANGIANA
Performs comparison between H0 (LCDM) and H1 (UCS Scalar Field)
Calculates Information Criteria (AIC, BIC) for model selection
"""

import numpy as np
import pandas as pd
from scipy import stats
from run_ucs_model import UCSModel, load_observational_data
import matplotlib.pyplot as plt


class StatisticalValidator:
    """
    Validator for cosmological models using observational data
    """
    
    def __init__(self, data_path):
        """
        Initialize with observational dataset
        """
        self.z_obs, self.H_obs, self.H_err = load_observational_data(data_path)
        if self.z_obs is None:
            # Generate synthetic data if file missing (for demonstration)
            self.z_obs = np.linspace(0.1, 2.0, 30)
            H_true = 67.4 * np.sqrt(0.3 * (1 + self.z_obs)**3 + 0.7)
            self.H_err = 0.05 * H_true
            self.H_obs = H_true + np.random.normal(0, self.H_err)
            self.is_synthetic = True
        else:
            self.is_synthetic = False

    def calculate_aic_bic(self, chi2, k, n):
        """
        Calculate AIC and BIC
        AIC = chi2 + 2k
        BIC = chi2 + k*ln(n)
        
        Args:
            chi2: Minimum chi-squared
            k: Number of free parameters
            n: Number of data points
        """
        aic = chi2 + 2 * k
        bic = chi2 + k * np.log(n)
        return aic, bic

    def perform_comparison(self):
        """
        Compare UCS Model (H1) vs LCDM (H0)
        """
        n = len(self.z_obs)
        
        # 1. Evaluate LCDM (H0)
        # Parameters: Omega_m, H0 (k=2)
        h0_model = UCSModel(lambda_param=0.0, omega_m=0.3, h0=67.4)
        chi2_h0, _ = h0_model.chi_squared(self.z_obs, self.H_obs, self.H_err)
        aic_h0, bic_h0 = self.calculate_aic_bic(chi2_h0, 2, n)
        
        # 2. Evaluate UCS Model (H1)
        # Parameters: lambda, Omega_m, H0 (k=3)
        h1_model = UCSModel(lambda_param=0.1, omega_m=0.3, h0=67.4)
        chi2_h1, _ = h1_model.chi_squared(self.z_obs, self.H_obs, self.H_err)
        aic_h1, bic_h1 = self.calculate_aic_bic(chi2_h1, 3, n)
        
        # 3. Delta metrics
        delta_aic = aic_h1 - aic_h0
        delta_bic = bic_h1 - bic_h0
        
        results = {
            "n_points": n,
            "H0_LCDM": {"chi2": chi2_h0, "aic": aic_h0, "bic": bic_h0},
            "H1_UCS": {"chi2": chi2_h1, "aic": aic_h1, "bic": bic_h1},
            "delta_aic": delta_aic,
            "delta_bic": delta_bic
        }
        
        return results

    def print_report(self, res):
        """
        Print formatted statistical report
        """
        print("="*60)
        print("STATISTICAL VALIDATION REPORT: UCS-LAGRANGIANA")
        print("="*60)
        print(f"Dataset: {'Synthetic (Generated)' if self.is_synthetic else 'Pantheon Survey'}")
        print(f"Number of observations (n): {res['n_points']}")
        print("-"*60)
        
        print(f"{'Metric':<15} | {'LCDM (H0)':<15} | {'UCS (H1)':<15}")
        print("-"*60)
        print(f"{'Chi-squared':<15} | {res['H0_LCDM']['chi2']:<15.4f} | {res['H1_UCS']['chi2']:<15.4f}")
        print(f"{'AIC':<15} | {res['H0_LCDM']['aic']:<15.4f} | {res['H1_UCS']['aic']:<15.4f}")
        print(f"{'BIC':<15} | {res['H0_LCDM']['bic']:<15.4f} | {res['H1_UCS']['bic']:<15.4f}")
        print("-"*60)
        
        print(f"
Model Selection Criteria:")
        print(f"  ΔAIC (H1 - H0) = {res['delta_aic']:.4f}")
        print(f"  ΔBIC (H1 - H0) = {res['delta_bic']:.4f}")
        
        # Interpretation
        print("
Interpretation (Jeffreys' Scale):")
        if res['delta_aic'] < -2:
            print("  - Evidence favors UCS Model (H1) over LCDM.")
        elif res['delta_aic'] > 2:
            print("  - Evidence favors LCDM (H0) over UCS Model.")
        else:
            print("  - No significant preference between models.")
            
        print("="*60)


def main():
    """
    Main statistical analysis execution
    """
    import os
    from pathlib import Path
    
    # Path to data
    data_path = Path(__file__).parent / "data" / "H_z_data.csv"
    
    # Initialize validator
    validator = StatisticalValidator(data_path)
    
    # Run comparison
    results = validator.perform_comparison()
    
    # Print report
    validator.print_report(results)


if __name__ == "__main__":
    main()
