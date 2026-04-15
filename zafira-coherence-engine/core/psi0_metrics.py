def compute_system_performance(results):
    if not results:
        return 0.0
    return sum(r["score"] for r in results) / len(results)
