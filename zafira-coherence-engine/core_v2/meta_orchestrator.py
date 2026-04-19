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

        if "x" in task_l or "=" in task_l:
            return "algebra"
        elif "%" in task_l or "calcule" in task_l:
            return "numeric"
        elif "explique" in task_l:
            return "explanation"
        else:
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
