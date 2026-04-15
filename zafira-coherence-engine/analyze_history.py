import json
import os
from collections import Counter

LOG_FILE = "/home/ubuntu/psi0-budget-system/logs/system_history.json"

def analyze():
    if not os.path.exists(LOG_FILE):
        print("Erro: Arquivo de histórico não encontrado.")
        return

    with open(LOG_FILE, "r") as f:
        history = json.load(f)

    total_cycles = len(history)
    if total_cycles == 0:
        print("Histórico vazio.")
        return

    # 1. Taxa de Sucesso Global
    successes = [h for h in history if h.get("global_score", 0) >= 0.8]
    success_rate = (len(successes) / total_cycles) * 100

    # 2. Métrica de Resiliência (Sucesso em Modo de Degradação)
    degraded_cycles = [h for h in history if "MODO DEGRADAÇÃO" in h.get("reason", "")]
    degraded_successes = [h for h in degraded_cycles if h.get("global_score", 0) >= 0.8]
    resilience_rate = (len(degraded_successes) / len(degraded_cycles)) * 100 if degraded_cycles else 100

    # 3. Análise de Falhas por Tipo
    failure_types = Counter([h.get("failure_type") for h in history if h.get("failure_type") != "none"])
    
    # 4. Incerteza Média
    avg_uncertainty = sum([h.get("uncertainty", 0) for h in history]) / total_cycles

    # 5. Taxa de Recuperação (Uso de LLM como reforço cognitivo)
    recovery_cycles = [h for h in history if h.get("executor") == "llm"]
    recovery_rate = (len(recovery_cycles) / total_cycles) * 100

    # Relatório
    print("="*70)
    print("📊 RELATÓRIO DE RESILIÊNCIA OPERACIONAL ψ₀")
    print("="*70)
    print(f"Total de Ciclos Analisados: {total_cycles}")
    print(f"Taxa de Sucesso Global: {success_rate:.1f}%")
    print(f"RESILIÊNCIA (Sucesso em Degradação): {resilience_rate:.1f}%")
    print(f"Taxa de Recuperação (Reforço Cognitivo): {recovery_rate:.1f}%")
    print(f"Incerteza Média do Sistema: {avg_uncertainty:.2f}")
    print("-" * 70)
    print("🔍 ANÁLISE DE FALHAS ADVERSARIAIS:")
    if not failure_types:
        print("  - Nenhuma falha crítica detectada.")
    for f_type, count in failure_types.items():
        print(f"  - {f_type.upper()}: {count} ocorrências (Degradação Graciosa Ativada)")
    
    print("-" * 70)
    print("⚙️ COMPORTAMENTO DO ORQUESTRADOR:")
    reasons = Counter([h.get("reason").split(":")[0] for h in history])
    for reason, count in reasons.items():
        print(f"  - {reason}: {count} ({ (count/total_cycles)*100 :.1f}%)")
    
    print("-" * 70)
    print("🧬 VEREDITO DE ENGENHARIA DE SISTEMAS:")
    if resilience_rate >= 90 and avg_uncertainty > 0.5:
        print("✅ SISTEMA RESILIENTE: O sistema falha de forma previsível e recupera com coerência.")
    elif resilience_rate >= 70:
        print("⚠️ SISTEMA EM ADAPTAÇÃO: Resiliência aceitável, mas requer ajuste no detector de incerteza.")
    else:
        print("❌ SISTEMA FRÁGIL: Falha catastrófica detectada em ambiente hostil.")
    print("="*70)

if __name__ == "__main__":
    analyze()
