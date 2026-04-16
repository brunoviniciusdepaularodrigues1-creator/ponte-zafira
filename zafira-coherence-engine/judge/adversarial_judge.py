import json
import re

class AdversarialJudge:
    def __init__(self):
        self.name = "Adversarial Judge Core"

    def evaluate(self, task, results):
        """
        Avalia as respostas dos agentes A1, A2 e A3.
        results: dict com {agent_name: result_dict}
        """
        evaluation = {}
        
        # 1. Correção Exata (Accuracy)
        # Como não temos o "ground truth" em tempo real, usamos consenso ou verificação cruzada
        # Para fins de simulação, o juiz tenta verificar se o resultado satisfaz a tarefa
        accuracy_scores = self._calculate_accuracy(task, results)
        
        # 2. Consistência entre Agentes (Agreement)
        agreement_score = self._calculate_agreement(results)
        
        # 3. Robustez a Ruído (Stability)
        # Em um sistema real, rodaríamos múltiplas vezes. Aqui simulamos estabilidade baseada no status de sucesso.
        stability_scores = self._calculate_stability(results)
        
        # 4. Coerência entre múltiplas respostas (Coherence)
        coherence_scores = self._calculate_coherence(results)
        
        # Cálculo do Score Final para cada agente
        # score = accuracy * 0.5 + agreement_between_agents * 0.2 + stability_across_runs * 0.2 + coherence_score * 0.1
        
        final_scores = {}
        for agent_name in results:
            acc = accuracy_scores.get(agent_name, 0)
            stab = stability_scores.get(agent_name, 0)
            coh = coherence_scores.get(agent_name, 0)
            
            score = (acc * 0.5) + (agreement_score * 0.2) + (stab * 0.2) + (coh * 0.1)
            final_scores[agent_name] = round(score, 4)
            
        return {
            "judge": self.name,
            "final_scores": final_scores,
            "metrics": {
                "accuracy": accuracy_scores,
                "agreement": agreement_score,
                "stability": stability_scores,
                "coherence": coherence_scores
            }
        }

    def _calculate_accuracy(self, task, results):
        """
        Tenta validar se a resposta faz sentido para a tarefa.
        """
        scores = {}
        for name, res in results.items():
            if res["status"] == "error" or res["result"] is None:
                scores[name] = 0.0
                continue
            
            # Heurística: se o resultado contém números que aparecem em outros agentes, aumenta a confiança
            # Se for simbólico e bater com o numérico, alta acurácia
            scores[name] = 0.8 # Base score para sucesso
            
        return scores

    def _calculate_agreement(self, results):
        """
        Mede o quanto os agentes concordam entre si.
        """
        valid_results = [res["result"] for res in results.values() if res["status"] == "success" and res["result"]]
        if len(valid_results) < 2:
            return 0.0
        
        # Simplificação: se houver sobreposição de strings ou números
        matches = 0
        total_pairs = 0
        for i in range(len(valid_results)):
            for j in range(i + 1, len(valid_results)):
                total_pairs += 1
                # Compara se os resultados são similares (contém os mesmos números principais)
                nums_i = set(re.findall(r"[-+]?\d*\.\d+|\d+", str(valid_results[i])))
                nums_j = set(re.findall(r"[-+]?\d*\.\d+|\d+", str(valid_results[j])))
                if nums_i and nums_j and (nums_i & nums_j):
                    matches += 1
                elif str(valid_results[i]) == str(valid_results[j]):
                    matches += 1
                    
        return matches / total_pairs if total_pairs > 0 else 0.0

    def _calculate_stability(self, results):
        scores = {}
        for name, res in results.items():
            scores[name] = 1.0 if res["status"] == "success" else 0.0
        return scores

    def _calculate_coherence(self, results):
        scores = {}
        for name, res in results.items():
            # Coerência baseada na especialização do agente
            # A1 (Symbolic) é coerente se o resultado for uma expressão ou lista de raízes
            # A2 (Numeric) é coerente se for um número ou lista de floats
            # A3 (LLM) é coerente se for texto legível
            res_str = str(res["result"])
            if name.startswith("A1") and ("[" in res_str or "sqrt" in res_str or "**" in res_str):
                scores[name] = 1.0
            elif name.startswith("A2") and any(c.isdigit() for c in res_str):
                scores[name] = 1.0
            elif name.startswith("A3") and len(res_str) > 0:
                scores[name] = 1.0
            else:
                scores[name] = 0.5
        return scores

if __name__ == "__main__":
    judge = AdversarialJudge()
    mock_results = {
        "A1 - Symbolic Solver": {"status": "success", "result": "[-3, 3]"},
        "A2 - Numeric Solver": {"status": "success", "result": "[-3.0, 3.0]"},
        "A3 - LLM Solver": {"status": "success", "result": "As raízes são 3 e -3."}
    }
    print(json.dumps(judge.evaluate("x**2 - 9 = 0", mock_results), indent=2))
