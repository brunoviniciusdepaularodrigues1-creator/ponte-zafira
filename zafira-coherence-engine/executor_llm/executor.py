import json
import time
import os
import datetime

# Caminho para a interface de ponte (um nível acima)
BRIDGE_FILE = "../bridge_interface.json"
OUTPUT_FILE = "execution_result_llm.json"

def evaluate_execution(result):
    # O LLM recebe um score base alto para tarefas complexas (C ou F)
    if "LLM_PROCESSOU" in result:
        return 0.95
    return 0.3

def execute_action(decision):
    stage = decision["stage"]
    content = decision["input"]

    # Simulação de processamento cognitivo (depois pode ser conectado a uma API real)
    if stage in ["C", "F"]:
        return f"LLM_PROCESSOU (Cognição): {content.strip()}"
    
    return f"LLM_PROCESSOU (Simples): {content.strip()}"

def run():
    print("Executor Agent LLM iniciado (Camada Cognitiva)...")

    while True:
        try:
            if os.path.exists(BRIDGE_FILE):
                with open(BRIDGE_FILE, "r") as f:
                    data = json.load(f)

                decision = data["best_decision"]

                result = execute_action(decision)
                score = evaluate_execution(result)

                with open(OUTPUT_FILE, "w") as f:
                    json.dump({
                        "executor": "llm",
                        "result": result,
                        "score": score,
                        "timestamp": datetime.datetime.now().isoformat(),
                        "source": decision
                    }, f, indent=2, ensure_ascii=False)

                print(f"LLM executou: {result} | Score: {score}")
            else:
                print("LLM aguardando bridge_interface.json...")

        except Exception as e:
            print(f"Erro no Executor LLM: {e}")

        time.sleep(5)

if __name__ == "__main__":
    run()
