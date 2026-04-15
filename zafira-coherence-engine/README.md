# zafira-coherence-engine — Motor de Coerência Universal

Este sistema é o motor de decisão e execução do ecossistema ψ₀, orquestrado pela Ponte Zafira. Ele implementa uma rede multiagente para processamento de tarefas de cosmologia e sistemas complexos, agora consolidado como o **Zafira Coherence Engine**.

## 🚀 Navegação Rápida

- **[Comece por aqui](MANIFESTO.md)** — Manifesto de Coerência e Propósito.
- **[Eixo Conceitual](SYSTEM_LIMITS.md)** — Blindagem ética e técnica do sistema.
- **[Eixo Técnico](core/)** — Núcleo de coerência, agentes e executores.
- **[Observabilidade](logs/system_history.json)** — Histórico global de eventos e performance.

## ⚙️ Arquitetura de Infraestrutura Distribuída

O sistema evoluiu para uma rede de inteligência distribuída com meta-orquestração:

1.  **Ponte Zafira (Meta-Orquestradora):** Analisa a complexidade do input e seleciona o nó ψ₀ mais adequado.
2.  **Nós ψ₀ Especializados:**
    - **Nó 1 (Conservador):** Focado em estabilidade e ações técnicas de alta coerência.
    - **Nó 2 (Exploratório):** Especializado em lidar com o Caos (C) e inputs complexos.
    - **Nó 3 (Analítico):** Equilíbrio entre estruturação e validação técnica.
3.  **Orquestração de Execução:** A Ponte seleciona o executor (V1, V2, LLM) baseado na decisão do nó.
4.  **Executores:** Processam a tarefa e alimentam a camada de observabilidade.

## 📊 Camada de Observabilidade

O sistema agora conta com uma camada de observabilidade ativa que registra cada ciclo de decisão no arquivo `logs/system_history.json`. Para analisar a performance do sistema, utilize o script:

```bash
python3 analyze_history.py
```

Este script fornece métricas sobre a taxa de sucesso, distribuição de estágios e eficiência de cada executor, garantindo que o sistema seja validado antes de qualquer expansão de escala.
