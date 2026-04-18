import json
import os
import random
from datetime import datetime

class Psi0Node:
    def __init__(self, node_dir):
        self.node_dir = node_dir
        with open(os.path.join(node_dir, "config.json"), "r") as f:
            self.config = json.load(f)
        
    def process_input(self, input_data):
        """
        Simula a decisão do nó ψ₀ baseada em seu perfil.
        """
        complexity = input_data.get("complexity", 0.5)
        coherence = input_data.get("coherence", 0.5)
        
        # Lógica de decisão baseada no perfil
        if self.config["profile"] == "Conservador":
            stage = "A" if coherence > 0.7 else "F"
        elif self.config["profile"] == "Exploratório":
            stage = "C" if complexity > 0.6 else "F"
        else: # Analítico
            stage = "V" if 0.4 < complexity < 0.8 else "L"
            
        decision = {
            "node_id": self.config["node_id"],
            "profile": self.config["profile"],
            "timestamp": datetime.now().isoformat(),
            "best_decision": {
                "input": input_data["text"],
                "stage": stage,
                "coherence": coherence,
                "complexity": complexity
            }
        }
        
        # Salva na interface de ponte do nó
        bridge_path = os.path.join(self.node_dir, "bridge_interface.json")
        with open(bridge_path, "w") as f:
            json.dump(decision, f, indent=2, ensure_ascii=False)
            
        return decision

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Uso: python3 psi0_node_runner.py <node_dir> <input_text>")
        sys.exit(1)
        
    node = Psi0Node(sys.argv[1])
    input_data = {"text": sys.argv[2], "complexity": random.random(), "coherence": random.random()}
    result = node.process_input(input_data)
    print(f"Nó {result['node_id']} ({result['profile']}) decidiu: {result['best_decision']['stage']}")
