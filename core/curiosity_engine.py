import numpy as np

class CuriosityEngine:
    """
    Curiosity Engine Nível 12: Mede o ganho de informação (Surpresa).
    Implementa o Curiosity Bound para evitar exploração de ruído inútil.
    """
    def __init__(self, bound=0.05):
        self.bound = bound
        self.knowledge_base = {} # {task_type: last_score}
        self.information_gain_history = []

    def measure_surprise(self, task_type, score):
        """Mede a diferença entre o score esperado e o real."""
        last_score = self.knowledge_base.get(task_type, 0.5)
        surprise = abs(score - last_score)
        
        # Atualiza a base de conhecimento
        self.knowledge_base[task_type] = (last_score * 0.9) + (score * 0.1)
        return surprise

    def is_worth_exploring(self, task_type):
        """Aplica o Curiosity Bound."""
        # Se não conhecemos a tarefa, vale a pena explorar
        if task_type not in self.knowledge_base:
            return True
        
        # Se o ganho de informação recente for muito baixo, para de explorar
        recent_gain = self.knowledge_base[task_type]
        # Se já atingimos alta performance (> 0.9), o ganho marginal é baixo
        if recent_gain > 0.9:
            return False
            
        return True

    def get_curiosity_signal(self, task_type):
        """Retorna um sinal de bônus para tarefas com alta incerteza."""
        if task_type not in self.knowledge_base:
            return 0.3 # Bônus máximo para o desconhecido
        
        # Bônus inversamente proporcional ao conhecimento
        return 0.3 * (1.0 - self.knowledge_base[task_type])
