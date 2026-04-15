def stability_metric(history):
    Cs = [h["C"] for h in history]
    return sum(Cs) / len(Cs)
