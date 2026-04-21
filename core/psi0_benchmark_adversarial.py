ADVERSARIAL_BENCHMARK = [
    # Tarefas com múltiplas soluções
    {
        "id": "adv_1",
        "input": "resolve x^2 = 9",
        "ground_truth": 3,  # aceita 3 ou -3
        "alt_truth": [-3, 3]
    },
    # Tarefas com ruído
    {
        "id": "adv_2",
        "input": "resolve x + 2 = 5 (considere margem de erro)",
        "ground_truth": 3,
        "alt_truth": [3]
    },
    # Tarefas enganosas
    {
        "id": "adv_3",
        "input": "0.1 + 0.2",
        "ground_truth": 0.3,
        "alt_truth": [0.3]
    },
    # Tarefas de múltiplos passos
    {
        "id": "adv_4",
        "input": "resolve 2*x + 3 = 15",
        "ground_truth": 6,
        "alt_truth": [6]
    },
    # Ambiguidade
    {
        "id": "adv_5",
        "input": "resolve x*x - 4 = 0",
        "ground_truth": 2,
        "alt_truth": [-2, 2]
    },
    # Problema não-trivial
    {
        "id": "adv_6",
        "input": "resolve 3*x - 7 = 2*x + 1",
        "ground_truth": 8,
        "alt_truth": [8]
    },
    # Operação com ponto flutuante (enganosa)
    {
        "id": "adv_7",
        "input": "1/3 * 3",
        "ground_truth": 1,
        "alt_truth": [1]
    },
    # Expressão complexa
    {
        "id": "adv_8",
        "input": "resolve x**2 - 5*x + 6 = 0",
        "ground_truth": 2,
        "alt_truth": [2, 3]
    }
]
