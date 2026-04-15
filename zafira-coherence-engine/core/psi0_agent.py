import time
import os
import sys
import json
import random
import math
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
        self.generation = 0
        # Caminho absoluto para garantir que o arquivo seja encontrado
        self.memory_file = os.path.abspath(os.path.join(os.path.dirname(__file__), "agent_memory.json"))
        self.memory = self._load_memory()

    def _load_memory(self):
        if os.path.exists(self.memory_file):
            with open(self.memory_file, "r") as f:
                return json.load(f)
        return {
            "decisions": [],
            "executor_performance": {"v1": [], "v2": [], "llm": []},
            "consequences": {} # Mapeia (stage, executor) -> avg_score
        }

    def _save_memory(self):
        with open(self.memory_file, "w") as f:
            json.dump(self.memory, f, indent=2)

    def internal_evaluate(self, executor, result_data, top_decision):
        """
        Avaliação Interna de Score:
        O próprio agente avalia se o resultado foi coerente com sua intenção original.
        """
        base_score = result_data.get("score", 0.5)
        stage = top_decision.get("stage", "F")
        coherence = top_decision.get("coherence", 0.5)
        
        # Penalização por desalinhamento de estágio
        penalty = 0
        if stage == "C" and executor == "v1": penalty = 0.2 # V1 é ruim para Caos
        if stage == "A" and executor == "llm": penalty = 0.1 # LLM é "caro" para Ação simples
        
        internal_score = (base_score * 0.6) + (coherence * 0.4) - penalty
        return round(max(0, min(1, internal_score)), 2)

    def select_strategy_probabilistic(self, top_decision, temperature=0.2):
        """
        Seleção Probabilística (Softmax):
        Permite exploração e aprendizado, evitando heurísticas fixas.
        """
        stage = top_decision.get("stage", "F")
        executors = ["v1", "v2", "llm"]
        
        # Calcula scores baseados na memória de consequências
        scores = []
        for exe in executors:
            key = f"{stage}_{exe}"
            perf = self.memory["consequences"].get(key, 0.5)
            scores.append(perf)
            
        # Softmax para probabilidades
        exp_scores = [math.exp(s / temperature) for s in scores]
        sum_exp = sum(exp_scores)
        probs = [e / sum_exp for e in exp_scores]
        
        chosen = random.choices(executors, weights=probs, k=1)[0]
        return chosen, probs

    def update_consequences(self, stage, executor, internal_score):
        key = f"{stage}_{executor}"
        if key not in self.memory["consequences"]:
            self.memory["consequences"][key] = internal_score
        else:
            # Média móvel para aprendizado contínuo
            alpha = 0.3
            self.memory["consequences"][key] = (1 - alpha) * self.memory["consequences"][key] + alpha * internal_score
        
        self.memory["executor_performance"][executor].append(internal_score)
        self._save_memory()

    def run(self):
        print("Zafira Coherence Engine: Psi0Agent Evolutivo Iniciado...")

        try:
            while True:
                print("\n--- Ciclo de Aprendizado Cognitivo ---")
                
                results = process()
                if not results:
                    print("Aguardando entradas...")
                    time.sleep(self.interval)
                    continue
                
                ranked = rank_results(results)
                save_results(ranked)
                top = ranked[0]

                # Seleção Probabilística
                chosen_executor, probs = self.select_strategy_probabilistic(top)
                print(f"Decisão: {top['input'][:30]}... | Stage: {top['stage']}")
                print(f"Seleção Probabilística: {chosen_executor} (Probs: {['%.2f' % p for p in probs]})")

                # Simulação de leitura de resultado (em um sistema real, isso esperaria a execução)
                # Para o loop, vamos ler o último resultado disponível
                internal_score = 0.5
                res_path = f"executor_{'agent' if chosen_executor=='v1' else ('agent_v2' if chosen_executor=='v2' else 'llm')}/execution_result{'_v2' if chosen_executor=='v2' else ('_llm' if chosen_executor=='llm' else '')}.json"
                
                if os.path.exists(res_path):
                    with open(res_path, "r") as f:
                        res_data = json.load(f)
                        internal_score = self.internal_evaluate(chosen_executor, res_data, top)
                
                # Aprendizado: Atualiza memória de consequências
                self.update_consequences(top["stage"], chosen_executor, internal_score)
                print(f"Aprendizado: Score Interno {internal_score} registrado para {chosen_executor} em {top['stage']}")

                # Exportar Estado
                bridge_data = {
                    "agent": "zafira-psi0",
                    "timestamp": datetime.now().isoformat(),
                    "chosen_executor": chosen_executor,
                    "internal_score": internal_score,
                    "probabilities": probs,
                    "memory_status": "updated"
                }

                with open("bridge_interface.json", "w") as f:
                    json.dump(bridge_data, f, indent=2, ensure_ascii=False)

                time.sleep(self.interval)
        except KeyboardInterrupt:
            print("\nPsi0Agent finalizado.")
