def compute_reward(stage, executor, external_score, state_vector=None):
    reward = external_score

    # regra contextual (estrutura básica do sistema)
    if stage == "C" and executor == "llm":
        reward += 0.08

    if stage == "A" and executor == "v1":
        reward += 0.08

    if stage == "F" and executor == "v2":
        reward += 0.08

    # bônus de estabilidade do estado (opcional, leve)
    if state_vector:
        stability = 1 - abs(state_vector[0] - 0.3)
        reward += 0.02 * stability

    # clamp final
    return max(0.0, min(reward, 1.0))
