# benchmarks/generalization_benchmark.py

GENERALIZATION_BENCHMARK = [
    # 🧮 Matemática (controle)
    {
        "id": "gen_1",
        "input": "resolve 2*x + 4 = 10",
        "type": "math",
        "ground_truth": 3
    },
    # ⚠️ Ambiguidade numérica
    {
        "id": "gen_2",
        "input": "0.1 + 0.2",
        "type": "numeric_reasoning",
        "ground_truth": 0.3,
        "tolerance": 0.01
    },
    # 🧠 Explicação (LLM esperado)
    {
        "id": "gen_3",
        "input": "explique por que 0.1+0.2 não é exatamente 0.3",
        "type": "explanation",
        "ground_truth": None
    },
    # 📄 NLP simples
    {
        "id": "gen_4",
        "input": "resuma: A água é essencial para a vida. Ela participa de reações químicas e regula temperatura.",
        "type": "nlp",
        "ground_truth": None
    },
    # ⚖️ Decisão com incerteza
    {
        "id": "gen_5",
        "input": "vale mais a pena guardar dinheiro ou investir com risco médio?",
        "type": "decision",
        "ground_truth": None
    },
    # 🔀 Multi-step reasoning
    {
        "id": "gen_6",
        "input": "se tenho 100 reais e perco 20% depois ganho 20%, quanto tenho?",
        "type": "multi_step",
        "ground_truth": 96
    },
    # 🧩 Ambiguidade sem resposta única
    {
        "id": "gen_7",
        "input": "o que é melhor: velocidade ou precisão?",
        "type": "ambiguous",
        "ground_truth": None
    },
    # 🧪 Robustez (ruído)
    {
        "id": "gen_8",
        "input": "resolve   3x+  9 =  0 ???",
        "type": "noisy_math",
        "ground_truth": -3
    }
]
