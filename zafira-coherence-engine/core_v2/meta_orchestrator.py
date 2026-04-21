class MetaOrchestrator:
    def __init__(self):
        self.memory = {
            "algebra": {},
            "numeric": {},
            "explanation": {},
            "unknown": {}
        }

    def classify_task(self, task):
        task_l = task.lower()
        # N18 Passo 4: Alinhamento com o EvolutionaryRouter
        if "explique" in task_l:
            return "explanation"
        if any(op in task_l for op in ["**", "x", "y", "z", "solve", "simplify", "="]):
            return "algebra"
        if any(op in task_l for op in ["%", "calcule", "dividido", "sqrt", "sin", "cos", "log", "exp"]) or any(c.isdigit() for c in task_l):
            return "numeric"
        return "unknown"

    def update(self, task, agent_type, reward):
        category = self.classify_task(task)

        if agent_type not in self.memory[category]:
            self.memory[category][agent_type] = []

        self.memory[category][agent_type].append(reward)

    def get_preference(self, task):
        category = self.classify_task(task)
        data = self.memory[category]

        if not data:
            return None

        avg = {k: sum(v)/len(v) for k, v in data.items()}
        return max(avg, key=avg.get)

    def get_summary(self):
        summary = {}
        for cat, agents in self.memory.items():
            summary[cat] = {k: round(sum(v)/len(v), 4) if v else 0 for k, v in agents.items()}
        return summary
