def rank_results(results):
    return sorted(
        results,
        key=lambda x: (
            x["coherence"],     # maior melhor
            x["structure"],     # maior melhor
            -x["variation"]     # menor melhor
        ),
        reverse=True
    )
