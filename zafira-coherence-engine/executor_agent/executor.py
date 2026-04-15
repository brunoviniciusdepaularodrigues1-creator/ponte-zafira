import json
import time
import os
import datetime

# Caminho para a interface de ponte (um nível acima)
BRIDGE_FILE = "../bridge_interface.json"
CONFIG_FILE = "config.json"
OUTPUT_FILE = "execution_result.json"

# Configuração padrão (será sobrescrita se config.json existir)
DEFAULT_CONFIG = {
    "length_weight": 0.3,
    "word_weight": 0.3,
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
    # Avaliação agora pode levar em conta a configuração
    if "EXECUTADO" in result:
        return 1.0
    if "REFINAR" in result:
        return 0.5
    return 0.2

def execute_action(decision, config):
    stage = decision["stage"]
    content = decision["input"]

    if stage == "A":
        return f"EXECUTADO: {content.strip()}"
    if stage == "F":
        return f"REFINAR: {content.strip()}"
    if stage == "C":
        return f"REORGANIZAR: {content.strip()}"
    return "SEM AÇÃO"

def run():
    print("Executor Agent V1 iniciado (Parametrizado)...")

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
                        "executor": "v1",
                        "config": config,
                        "result": result,
                        "score": score,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "source": decision
                    }, f, indent=2, ensure_ascii=False)

                print(f"V1 executou: {result} | Score: {score}")
            else:
                print("V1 aguardando bridge_interface.json...")

        except Exception as e:
            print(f"Erro no Executor V1: {e}")

        time.sleep(5)

if __name__ == "__main__":
    run()
