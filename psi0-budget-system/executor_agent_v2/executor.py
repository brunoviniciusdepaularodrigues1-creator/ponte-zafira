import json
import time
import os
import datetime

# Caminho para a interface de ponte (um nível acima)
BRIDGE_FILE = "../bridge_interface.json"
CONFIG_FILE = "config_v2.json"
OUTPUT_FILE = "execution_result_v2.json"

# Configuração padrão (será sobrescrita se config_v2.json existir)
DEFAULT_CONFIG = {
    "length_weight": 0.2,
    "word_weight": 0.4,
    "complexity_weight": 0.4
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return DEFAULT_CONFIG

def evaluate_execution(result, config):
    # V2 é mais rigoroso com o estágio 'A'
    if "PROCESSADO DIFERENTE" in result:
        return 0.9
    return 0.4

def execute_action(decision, config):
    stage = decision["stage"]
    content = decision["input"]

    # Comportamento especializado do V2
    if stage == "A":
        return f"PROCESSADO DIFERENTE: {content.strip()}"
    if stage == "F":
        return f"REFINAR V2: {content.strip()}"
    return "V2 SEM AÇÃO"

def run():
    print("Executor Agent V2 iniciado (Parametrizado)...")

    while True:
        try:
            config = load_config()
            if os.path.exists(BRIDGE_FILE):
                with open(BRIDGE_FILE, "r") as f:
                    data = json.load(f)

                decision = data["best_decision"]
                result = execute_action(decision, config)
                score = evaluate_execution(result, config)

                with open(OUTPUT_FILE, "w") as f:
                    json.dump({
                        "executor": "v2",
                        "config": config,
                        "result": result,
                        "score": score,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "source": decision
                    }, f, indent=2, ensure_ascii=False)

                print(f"V2 executou: {result} | Score: {score}")
            else:
                print("V2 aguardando bridge_interface.json...")

        except Exception as e:
            print(f"Erro no Executor V2: {e}")

        time.sleep(5)

if __name__ == "__main__":
    run()
