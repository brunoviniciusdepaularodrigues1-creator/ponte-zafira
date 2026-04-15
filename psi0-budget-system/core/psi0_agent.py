import time
import os
import sys
import json
from datetime import datetime

# Adiciona a raiz do projeto ao sys.path para permitir imports de core
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from core.psi0_executor import process, save_results
from core.psi0_ranker import rank_results
from core.executor_mutator import create_variant

# Arquivos de feedback dos múltiplos executores (Rede Heterogênea)
FEEDBACK_FILES = [
    "executor_agent/execution_result.json",
    "executor_agent_v2/execution_result_v2.json",
    "executor_llm/execution_result_llm.json"
]

class Psi0Agent:
    def __init__(self, interval=5):
        self.interval = interval
        self.executor_history = {} # Memória histórica dos executores
        self.generation = 0

    def read_all_feedbacks(self):
        feedbacks = []
        for f_path in FEEDBACK_FILES:
            try:
                if os.path.exists(f_path):
                    with open(f_path, "r") as f:
                        data = json.load(f)
                        executor_id = data.get("executor", "v1" if "v1" in f_path else ("v2" if "v2" in f_path else "llm"))
                        score = data.get("score", 0.5)
                        config = data.get("config", {})
                        feedbacks.append({
                            "executor": executor_id, 
                            "score": score,
                            "config": config
                        })
                        
                        if executor_id not in self.executor_history:
                            self.executor_history[executor_id] = []
                        self.executor_history[executor_id].append(score)
            except Exception as e:
                print(f"Erro ao ler feedback de {f_path}: {e}")
        return feedbacks

    def select_best_strategy(self, feedbacks, top_decision):
        if not feedbacks:
            return "v1", 0.5, {}
        
        # Lógica Híbrida: Se a tarefa for Caos (C) ou Forma (F), prioriza LLM se disponível
        stage = top_decision.get("stage", "F")
        if stage in ["C", "F"]:
            llm_feedback = next((f for f in feedbacks if f["executor"] == "llm"), None)
            if llm_feedback:
                return llm_feedback["executor"], llm_feedback["score"], llm_feedback["config"]

        # Caso contrário, seleciona o executor com o melhor score
        best = max(feedbacks, key=lambda x: x["score"])
        return best["executor"], best["score"], best["config"]

    def spawn_variant(self, best_config):
        # Gera uma nova variante baseada na melhor configuração atual (apenas para executores evolutivos)
        new_config = create_variant(best_config)
        self.generation += 1
        
        config_path = "executor_agent_v2/config_v2.json"
        try:
            with open(config_path, "w") as f:
                json.dump(new_config, f, indent=2)
            print(f"🧬 Nova variante gerada (Geração {self.generation}) aplicada ao V2.")
            return new_config
        except Exception as e:
            print(f"Erro ao gerar variante: {e}")
        return None

    def run(self):
        print("ψ₀ Agent iniciado (Arquitetura Cognitiva Híbrida)...")

        try:
            while True:
                print("\n--- Ciclo Cognitivo Híbrido ---")
                
                print("Processando entradas e rankeando...")
                results = process()
                if not results:
                    print("Nenhuma entrada encontrada.")
                    time.sleep(self.interval)
                    continue
                
                ranked = rank_results(results)
                save_results(ranked)
                top = ranked[0]

                print(f"Melhor Input: {top['input'].strip()} | Stage: {top['stage']}")

                print("Avaliando rede de executores (Simples, Evolutivo, LLM)...")
                feedbacks = self.read_all_feedbacks()
                best_executor, best_score, best_config = self.select_best_strategy(feedbacks, top)
                
                print(f"Estratégia Selecionada: {best_executor} | Score Esperado: {best_score}")

                # Evolução guiada (apenas se o melhor for um executor evolutivo)
                if best_executor != "llm" and best_score > 0.8 and best_config:
                    self.spawn_variant(best_config)

                # Exportar para a Interface de Ponte (Bridge Interface)
                bridge_data = {
                    "agent": "psi0",
                    "timestamp": datetime.now().isoformat(),
                    "generation": self.generation,
                    "best_executor": best_executor,
                    "feedback_applied": best_score,
                    "best_decision": top,
                    "ranking": ranked,
                    "network_status": feedbacks
                }

                with open("bridge_interface.json", "w") as f:
                    json.dump(bridge_data, f, indent=2, ensure_ascii=False)

                print(f"Aguardando {self.interval} segundos para o próximo ciclo cognitivo...")
                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nψ₀ Agent finalizado pelo usuário.")
