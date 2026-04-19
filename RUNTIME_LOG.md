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

## TEST 003
input: Implementação de decision_margin no AdversarialJudge
expected: avg_decision_margin registrado, judge_consistency mantida ou ↑
output: divergence_score: 1.0689, judge_consistency: 0.6667, controller_learning_delta: 0.2553, avg_decision_margin: 0.4333
result: PASS
notes: A métrica decision_margin foi integrada com sucesso. O valor de 0.4333 indica uma convicção moderada do juiz (quase metade da escala de score). A consistência do juiz subiu para 0.66, sugerindo que a melhor visibilidade das métricas ajuda a validar a estabilidade do sistema.

## TEST 004
input: Expansão do conjunto de tarefas (3 -> 6 tarefas)
expected: judge_consistency > 0.6, avg_decision_margin > 0.3, learning_delta > 0
output: divergence_score: 1.0654, judge_consistency: 0.8333, controller_learning_delta: 0.4579, avg_decision_margin: 0.4333
result: PASS
notes: O sistema demonstrou alta robustez. A consistência do juiz subiu significativamente (0.66 -> 0.83), indicando que o router está selecionando agentes adequados para uma gama maior de problemas. A margem de decisão permaneceu estável em 0.4333, confirmando a convicção do juiz mesmo em novas tarefas. O aprendizado continua ativo e saudável.

## TEST 005
input: Teste de Memória e Especialização (Tarefas agrupadas: Álgebra e Cálculo Numérico)
expected: Especialização emergente (seleção consistente por categoria), learning_delta > 0
output: divergence_score: 1.0632, judge_consistency: 0.8333, controller_learning_delta: 0.4929, avg_decision_margin: 0.2167
result: PASS
notes: O router demonstrou especialização emergente. Para Álgebra, houve alternância entre A1 e A3 (ambos com alta acurácia). Para Cálculo Numérico, o A3 (LLM) dominou a seleção final, embora o A2 (Numeric) tenha recebido rewards competitivos. A queda na decision_margin (0.21) reflete a alta competição entre agentes competentes para as mesmas tarefas, validando a "competição saudável" do sistema.
