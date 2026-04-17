# Guia de Execução Científica

## 🚀 Como Rodar o Sistema
Para replicar os resultados do Nível 8 e validar a coerência do motor Zafira, siga os passos abaixo:

### 1. Preparação do Ambiente
```bash
# Instalar dependências
pip install -r requirements.txt
```

### 2. Execução dos Agentes
O motor pode ser iniciado através do `core/psi0_agent.py`. Ele irá coordenar os agentes simbólico, numérico e de linguagem.
```bash
python core/psi0_agent.py
```

### 3. Validação de Benchmarks
Para rodar os testes adversariais e verificar a resiliência do sistema:
```bash
python benchmarks/run_adversarial.py
```

### 4. Análise de Logs
Os resultados detalhados de cada ciclo de aprendizado são salvos em `logs/system_history.json`. Use o `RESULTADO.md` como referência para comparar as métricas obtidas.

---
**Nota:** O sistema opera sob o Axioma VII de Traçabilidade Total. Cada execução gera um rastro verificável.
