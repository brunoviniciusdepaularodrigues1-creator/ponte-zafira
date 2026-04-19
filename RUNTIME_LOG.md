# RUNTIME LOG

## TEST 001
input: x**2 - 16 = 0, Qual é a raiz quadrada de 144?, Explique a teoria da relatividade em uma frase.
expected: divergence_score > 0, judge_consistency > 0.5, controller_learning_delta > 0
output: divergence_score: 1.0648, judge_consistency: 0.6000, controller_learning_delta: 0.2729
result: PASS
notes: O loop multiagente N17.2 está operacional e gerando evidências de aprendizado e divergência.

## TEST 002
input: Ajuste de temperatura no EvolutionaryRouter (T=0.7)
expected: divergence_score ↓, judge_consistency ↑, controller_learning_delta mantido ou ↑
output: divergence_score: 1.0681, judge_consistency: 0.6154, controller_learning_delta: 0.5291
result: PASS (Parcial)
notes: A consistência do juiz subiu levemente (0.60 -> 0.615), mas a divergência permaneceu estável (1.06). O aprendizado (delta) dobrou, indicando que a temperatura menor ajudou a consolidar a política sem sacrificar a competição entre agentes.

## Rules
- Ran system -> register test result.
- Changed code/config -> register before/after behavior.
- Strange behavior -> register anomaly and suspected cause.
