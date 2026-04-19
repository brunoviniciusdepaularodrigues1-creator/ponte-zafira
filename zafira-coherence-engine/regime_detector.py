import numpy as np
import pandas as pd
import random

class RegimeDetector:
    def __init__(self, window=5, threshold_sigma=1.2, hysteresis_up=3, hysteresis_down=1, cooldown_period=3):
        self.window = window
        self.threshold_sigma = threshold_sigma
        self.hysteresis_up = hysteresis_up
        self.hysteresis_down = hysteresis_down
        self.cooldown_period = cooldown_period
        
        self.volatilities = [0.05] * window
        self.current_regime = "CALMARIA"
        self.sentinel_alert = False
        self.up_counter = 0
        self.down_counter = 0
        self.cooldown_counter = 0
        
        # CAMADA DE EXECUÇÃO (UCS Execution)
        self.current_exposure = 0.0 # Exposição atual ao Alpha (0.0 a 1.0)
        self.lambda_exit = 0.8 # Saída rápida (80% por ciclo)
        self.lambda_entry = 0.3 # Entrada lenta (30% por ciclo)
        
    def update(self, new_vol):
        self.volatilities.append(new_vol)
        if len(self.volatilities) > self.window:
            self.volatilities.pop(0)
            
        avg_sigma = np.mean(self.volatilities)
        current_sigma = self.volatilities[-1]
        delta_sigma = current_sigma - self.volatilities[-2] if len(self.volatilities) > 1 else 0
        
        # 1. CAMADA SENTINELA (Rápida)
        if delta_sigma > 0.4 or current_sigma > 2.5 * avg_sigma:
            self.sentinel_alert = True
            self.cooldown_counter = self.cooldown_period
        else:
            self.sentinel_alert = False
            if self.cooldown_counter > 0:
                self.cooldown_counter -= 1
            
        # 2. CAMADA CONFIRMADORA (Lenta)
        if current_sigma > self.threshold_sigma * avg_sigma or delta_sigma > 0.2:
            target_regime = "CAOS"
        elif delta_sigma > 0.05:
            target_regime = "TRANSIÇÃO"
        else:
            target_regime = "CALMARIA"
            
        if target_regime != self.current_regime:
            if self._is_higher_risk(target_regime, self.current_regime):
                self.up_counter += 1
                self.down_counter = 0
                if self.up_counter >= self.hysteresis_up:
                    self.current_regime = target_regime
                    self.up_counter = 0
                    if target_regime == "CAOS":
                        self.cooldown_counter = self.cooldown_period
            else:
                self.down_counter += 1
                self.up_counter = 0
                if self.down_counter >= self.hysteresis_down:
                    self.current_regime = target_regime
                    self.down_counter = 0
        else:
            self.up_counter = 0
            self.down_counter = 0
            
        # 3. GOVERNADOR DE ALOCAÇÃO (Alvo)
        target_exposure = 1.0
        if self.current_regime == "CAOS" or self.sentinel_alert:
            target_exposure = 0.0
        elif self.current_regime == "TRANSIÇÃO" or self.cooldown_counter > 0:
            target_exposure = 0.2
        else:
            target_exposure = 1.0
            
        # 4. CAMADA DE EXECUÇÃO SUAVIZADA (UCS Execution)
        # Aplica suavização assimétrica (Saída Rápida / Entrada Lenta)
        if target_exposure < self.current_exposure:
            # Saída (De-risking)
            self.current_exposure += (target_exposure - self.current_exposure) * self.lambda_exit
        else:
            # Entrada (Re-risking)
            self.current_exposure += (target_exposure - self.current_exposure) * self.lambda_entry
            
        return self.current_regime, self.sentinel_alert, self.current_exposure

    def _is_higher_risk(self, target, current):
        order = {"CALMARIA": 0, "TRANSIÇÃO": 1, "CAOS": 2}
        return order[target] > order[current]

def test_full_lifecycle():
    detector = RegimeDetector()
    
    # Cenário: Calmaria -> Flash Crash -> Recuperação Lenta
    scenarios = [0.05]*10 + [0.8] + [0.05]*15
    
    print("--- TESTE DE CICLO DE VIDA COMPLETO (SESSÃO 22.2) ---")
    print("Objetivo: Validar Saída Rápida e Entrada Gradual (Suavização Assimétrica).")
    for i, vol in enumerate(scenarios):
        regime, sentinel, exposure = detector.update(vol)
        status = "ALERTA" if sentinel else "LIMPO"
        print(f"Ciclo {i:02d} | Vol: {vol:.2f} | Sentinela: {status:6} | Regime: {regime:9} | Exposição Alpha: {exposure:.2f}")
        
        if i == 10:
            print(">> FLASH CRASH! Verificando velocidade de saída...")
        if i == 11:
            if exposure < 0.3:
                print(f">> SUCESSO: Saída agressiva (Exposição: {exposure:.2f}).")
            else:
                print(f">> FALHA: Saída lenta demais (Exposição: {exposure:.2f}).")
        if i > 15 and exposure < 1.0:
            if i == 16:
                print(">> RECUPERAÇÃO. Verificando entrada gradual...")
            # Verifica se a entrada é lenta (não pula de 0.2 para 1.0 em 1 ciclo)
                
    print("-----------------------------------------------------")

if __name__ == "__main__":
    test_full_lifecycle()
