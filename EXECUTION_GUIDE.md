# Guia de Execução Científica (Protocolo de Replicação)

Este guia fornece as instruções exatas para reproduzir os resultados do Nível 8 documentados no `RESULTADO.md`.

## 1. Requisitos do Sistema
- **Python:** 3.11+
- **Dependências:**
  ```text
  numpy>=1.24.0
  scipy>=1.10.0
  pandas>=2.0.0
  matplotlib>=3.7.0
  ```

## 2. Instalação
```bash
# Clone o repositório
gh repo clone brunoviniciusdepaularodrigues1-creator/ponte-zafira
cd ponte-zafira

# Instale as dependências
pip install -r requirements.txt
```

## 3. Ordem de Execução (Pipeline de Validação)

### Passo 1: Inicialização do Motor
Inicie o agente coordenador para carregar a MetaPolicy e os pesos dos atores.
```bash
python core/psi0_agent.py
```

### Passo 2: Execução de Benchmarks
Rode o harness de avaliação adversarial para gerar os dados brutos de performance.
```bash
python benchmarks/run_adversarial.py
```

### Passo 3: Cálculo de Entropia
Execute o script de análise para processar os logs e calcular a entropia de Shannon conforme a metodologia.
```bash
python core/psi0_benchmark.py --calculate-entropy
```

## 4. Verificação de Resultados
Os logs gerados em `logs/system_history.json` devem apresentar uma distribuição de ações que resulte em uma entropia $H \approx 0.06$. Qualquer desvio significativo (>10%) deve ser reportado como uma falha na replicação.

---
**Certificação:** Este protocolo segue o Axioma VII de Traçabilidade.

## 5. Validação do Loop Multi-Agente (N17.2)
Antes de evoluir arquitetura, valide o loop causal completo.

### Passo 4: Executar engine competitivo (gera log JSONL)
```bash
cd zafira-coherence-engine
PYTHONPATH=. python core_v2/psi0_loop_v2.py
```

### Passo 5: Medir reação do sistema
```bash
python validacao/validate_multiagent_loop.py --log agent_evolution_v75_log.txt
```

Registre o teste em `RUNTIME_LOG.md` com:
- input
- expected
- output
- result
- notes
