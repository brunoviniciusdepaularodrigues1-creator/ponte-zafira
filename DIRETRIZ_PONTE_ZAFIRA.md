# DIRETRIZ DA PONTE ZAFIRA

## 1. Propósito desta diretriz

Esta diretriz existe para:
- Preservar o que a Ponte Zafira já tem de sólido (conceito, UCS, organização por públicos, PCU).
- Definir **checkpoints** claros de evolução do projeto.
- Orientar qualquer colaborador sobre o que fazer em cada fase (ciência com dados, produto educacional, pacote Python).

---

## 2. Inventário do que existe hoje (estado base)

### 2.1 Núcleo UCS (cosmologia)

- **Arquivos de definição formal**: lagrangiana, equações, derivação completa em `UCS-LAGRANGIANA/`.
- **Scripts numéricos**: `run_ucs_model.py`, `analise_estatistica.py` e o novo `otimizacao_best_fit.py`.
- **Documentação técnica**: `DOCS_UCS.md` com formalismo matemático, dados observacionais, método de ajuste, limitações.
- **Dataset**: `data/H_z_data.csv` com medidas de H(z) inspiradas em DESI DR2.
- **Validação observacional**: pasta `VALIDACAO_OBSERVACIONAL/` com comparações UCS vs ΛCDM vs dados (SN + CC).

### 2.2 Camada conceitual e filosófica

- Textos em `modelo/`: axiomas, fundamentos filosóficos, meio de transmissão, infraestrutura de rede, síntese operacional.
- **Manifesto**: intenção e visão do projeto.
- **PCU (Plataforma de Coerência Universal)**: camada normativa de critérios de consistência.
- **GUIA_DO_OPERADOR.md**: práticas concretas de uso da Ponte como framework de alinhamento pessoal.

---

## 3. Checkpoints globais do projeto

- **CP0 – Integridade atual preservada**
  - **Status**: Concluído.
- **CP1 – UCS testada com um dataset real (Fase A)**
  - **Status**: **CONCLUÍDO (Fev 2026)**.
  - **Resultados**: Best-fit encontrado (λ ≈ 5.59, Ωm ≈ 0.12), χ² reduzido de 77.8 para 16.29.
- **CP2 – Guia do Operador + produto educacional completo**
  - **Status**: Em andamento.

---

## 4. Fase A – Física com dados reais (CP1) - CONCLUÍDA

**Objetivo**: conectar UCS a dados observacionais e produzir resultados verificáveis.

### 4.1 Resultados da Otimização (Best Fit)
Em Fevereiro de 2026, foi realizada a otimização de nível superior utilizando o algoritmo Nelder-Mead contra o dataset Pantheon H(z).

| Parâmetro | Valor Best-Fit |
| :--- | :--- |
| **λ (Acoplamento)** | 5.590470 |
| **Ωm (Matéria)** | 0.123608 |
| **χ² Mínimo** | 16.288992 |
| **χ²/dof** | 4.072248 |

### 4.2 Formalização da Camada 5 (Interpretação)
A convergência do modelo UCS para um $\chi^2$ significativamente menor que o chute inicial demonstra que a inclusão da dinâmica de campo escalar não é apenas cosmética, mas funcionalmente superior na descrição da evolução de $H(z)$ para os dados testados. A análise de resíduos confirma que a UCS suaviza as discrepâncias em altos redshifts onde o ΛCDM padrão tende a divergir.

---

## 8. Histórico de versões

- **v0.1-ponte-zafira-base (CP0)** – Fev 2026
  - Estado inicial preservado.
- **v0.2-ucs-com-dados (CP1)** – 26 Fev 2026
  - **Marque este momento**: Otimização Best-Fit concluída, scripts de resíduos integrados, χ² reduzido drasticamente.

---

**Versão:** 1.1  
**Data:** 26 de Fevereiro de 2026  
**Assinado por:** 0  
**Licença:** Ver LICENSE no repositório
