class MetaPolicy:

    def __init__(self):
        self.stats = {}
        self.task_types = ["algebra", "arithmetic", "reasoning"]
        for tt in self.task_types:
            self.stats[tt] = {
                "A1": {"correct": 0, "total": 0},
                "A2": {"correct": 0, "total": 0},
                "A3": {"correct": 0, "total": 0}
            }

    def update(self, task_type, action, reward):
        if task_type not in self.stats:
            self.stats[task_type] = {
                "A1": {"correct": 0, "total": 0},
                "A2": {"correct": 0, "total": 0},
                "A3": {"correct": 0, "total": 0}
            }
        self.stats[task_type][action]["total"] += 1

        if reward > 0.5:
            self.stats[task_type][action]["correct"] += 1

    def get_scores(self, task_type=None):
        scores = {}
        if task_type and task_type in self.stats:
            target_stats = self.stats[task_type]
        else:
            # Retorna scores globais se task_type não for especificado ou não encontrado
            global_stats = {"A1": {"correct": 0, "total": 0}, "A2": {"correct": 0, "total": 0}, "A3": {"correct": 0, "total": 0}}
            for tt_stats in self.stats.values():
                for agent, data in tt_stats.items():
                    global_stats[agent]["correct"] += data["correct"]
                    global_stats[agent]["total"] += data["total"]
            target_stats = global_stats

        for action, data in target_stats.items():
            if data["total"] == 0:
                scores[action] = 0.5
            else:
                scores[action] = data["correct"] / data["total"]

        return scores

    def best_action(self, task_type=None):
        scores = self.get_scores(task_type)
        if not scores: # Caso não haja scores, retorna None ou um default
            return None
        return max(scores, key=scores.get)

    def get_preference(self, task_type):
        # Retorna o agente com melhor histórico para a categoria de tarefa
        return self.best_action(task_type)
