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
- **Scripts numéricos**: `run_ucs_model.py` e `analise_estatistica.py`.
- **Documentação técnica**: `DOCS_UCS.md` com formalismo matemático, dados observacionais, método de ajuste, limitações.
- **Dataset**: `data/H_z_data.csv` com medidas de H(z) inspiradas em DESI DR2.
- **Validação observacional**: pasta `VALIDACAO_OBSERVACIONAL/` com comparações UCS vs ΛCDM vs dados (SN + CC).

### 2.2 Camada conceitual e filosófica

- Textos em `modelo/`: axiomas, fundamentos filosóficos, meio de transmissão, infraestrutura de rede, síntese operacional.
- **Manifesto**: intenção e visão do projeto.
- **PCU (Plataforma de Coerência Universal)**: camada normativa de critérios de consistência.
- **GUIA_DO_OPERADOR.md**: práticas concretas de uso da Ponte como framework de alinhamento pessoal.
- **Separação clara**: especulação organizada vs evidência mais robusta.

### 2.3 Organização do repositório

- **Navegação por público**: Filósofo/Pensador, Físico/Cientista, Desenvolvedor, Estudante.
- **Avisos de escopo**: "Este repositório **não faz afirmações sobre a realidade física fundamental**", "Este é um projeto exploratório e educacional".
- **Estrutura em camadas**: intenção → coerência → axiomas → UCS → formalização → dados → análise crítica.

> **Check inicial**: o estado descrito aqui está protegido pela tag `v0.1-ponte-zafira-base` (ver seção 7). Ajuste o nome da tag conforme você criar.

---

## 3. Checkpoints globais do projeto

Os checkpoints são marcos de versão que não devem ser reescritos.

- **CP0 – Integridade atual preservada**
  - Tag: `v0.1-ponte-zafira-base`.
  - Conteúdo: tudo o que está descrito na seção 2, funcionando.
  - **Status atual**: pronto para ser criado (este é o baseline).

- **CP1 – UCS testada com um dataset real**
  - Tag sugerida: `v0.2-ucs-com-dados`.
  - Conteúdo: scripts e resultados mínimos comparando UCS com conjunto de dados público, com análise χ², AIC, BIC.
  - **Status atual**: em andamento (dataset e scripts existem; falta rodar ajuste completo e documentar).

- **CP2 – Guia do Operador + produto educacional completo**
  - Tag sugerida: `v0.3-guia-educacional`.
  - Conteúdo: GUIA_DO_OPERADOR.md já existe; falta criar tutoriais práticos, VISAO_GERAL.md, GLOSSARIO.md, FAQ.md.
  - **Status atual**: parcialmente pronto.

- **CP3 – Pacote Python instalável básico**
  - Tag sugerida: `v0.4-pacote-python`.
  - Conteúdo: UCS empacotado em `src/pontezafira_ucs/`, com API simples e documentação mínima.
  - **Status atual**: não iniciado.

- **CP4 – Repo pronto para submissão / uso público amplo**
  - Tag sugerida: `v1.0-publico`.
  - Conteúdo: artigo esboçado ou pronto, tutoriais revisados, estrutura estável.
  - **Status atual**: futuro.

---

## 4. Fase A – Física com dados reais (CP1)

**Objetivo**: conectar UCS a dados observacionais e produzir resultados verificáveis.

### 4.1 Tarefas obrigatórias

- ✅ Dataset público já escolhido: `data/H_z_data.csv` (H(z) inspirado em DESI DR2).
- ✅ Script `run_ucs_model.py` e `analise_estatistica.py` já existem.
- ⏳ **Pendente**: rodar ajuste de parâmetros completo (MCMC ou grid search) e gerar:
  - Figura comparando H(z) UCS vs ΛCDM vs dados.
  - Tabela com χ², AIC, BIC.
  - Gráfico de w(z) (equação de estado).
- ⏳ **Pendente**: escrever seção "Resultados" em `VALIDACAO_OBSERVACIONAL/resultados_ucs.md` com:
  - Descrição do dataset usado.
  - Método de ajuste.
  - O que o modelo acerta, onde falha, principais limitações.

### 4.2 Documentação mínima da fase

- Criar `VALIDACAO_OBSERVACIONAL/README.md` descrevendo o processo de validação.
- Linkar `DOCS_UCS.md` para detalhes técnicos.

### 4.3 Checkpoint e versão

- Quando os itens 4.1 estiverem concluídos:
  - Criar tag `v0.2-ucs-com-dados`.
  - Adicionar uma linha na seção 8 (Histórico de versões) desta diretriz, com data e resumo.

---

## 5. Fase B – Produto educacional (CP2)

**Objetivo**: transformar a Ponte em ferramenta de estudo acessível.

### 5.1 Guia do Operador

- ✅ `GUIA_DO_OPERADOR.md` já existe e está bem estruturado.
- ⏳ **Pendente**: revisar e garantir links internos corretos.

### 5.2 Tutoriais práticos

- ⏳ Criar `tutoriais/ucs_exemplo_basico.md` com um roteiro completo:
  - Clonar o repositório.
  - Instalar dependências (`pip install numpy scipy matplotlib`).
  - Executar `run_ucs_model.py`.
  - Interpretar a saída com foco em aprendizado.

### 5.3 Arquivos de entrada do leitor

- ⏳ Criar `VISAO_GERAL.md`: introdução de 5 minutos ao projeto.
- ⏳ Criar `GLOSSARIO.md`: definições de termos técnicos (campo escalar, lagrangiana, ΛCDM, etc.).
- ⏳ Criar `FAQ.md`: perguntas frequentes.
- ✅ README.md já está bem organizado por público.

### 5.4 Checkpoint e versão

- Ao concluir 5.1 a 5.3:
  - Criar tag `v0.3-guia-educacional`.
  - Registrar na seção 8 desta diretriz.

---

## 6. Fase C – Pacote Python científico (CP3)

**Objetivo**: disponibilizar o núcleo UCS como biblioteca reutilizável.

### 6.1 Estrutura de pacote

- Criar diretório `src/pontezafira_ucs/` com:
  - `__init__.py`.
  - Módulos separados para equações, integração numérica, interface de alto nível.

### 6.2 API de alto nível

- Definir e documentar 2–3 funções principais, por exemplo:
  - `run_ucs_model(params, z_grid)`
  - `fit_ucs_to_data(dataset_path, initial_guess)`
- Garantir docstrings claras e exemplos mínimos.

### 6.3 Arquivos de empacotamento

- Adicionar `pyproject.toml` (ou `setup.cfg`) com:
  - Nome do pacote, versão, autor, descrição curta.
  - Dependências (numpy, scipy, matplotlib).
- Adicionar `LICENSE` apropriada (sugestão: MIT ou GPL-3.0).

### 6.4 Referência de API

- Criar `docs/API_REFERENCE.md` documentando brevemente:
  - Quais funções existem.
  - Quais parâmetros recebem.
  - Exemplos de uso básicos.

### 6.5 Checkpoint e versão

- Ao finalizar os passos 6.1–6.4:
  - Criar tag `v0.4-pacote-python`.
  - Registrar na seção 8.

---

## 7. Regras de preservação e versionamento

Para manter a integridade da Ponte Zafira ao longo do tempo:

- **Nunca reescrever um checkpoint**: sempre criar tags imutáveis para CP0, CP1, CP2, CP3, CP4.
- **Alterações grandes em textos de fundamento** (filosofia, definição da Ponte, PCU) devem ser feitas em branch separada, com comparação explícita antes de merge.
- **Antes de mudanças estruturais no código UCS**, garantir que a versão anterior está coberta por tag.
- **Opcional**: manter uma pasta `arquivo/` para versões antigas de textos conceituais que você quer preservar como "camada histórica".
- **Resultados negativos**: ajustes que falham, incompatibilidades com dados, devem ser preservados e documentados, não apagados. Isso é fundamental para a integridade científica.

---

## 8. Histórico de versões (preencher aos poucos)

Preencha esta lista conforme for atingindo cada marco.

- **v0.1-ponte-zafira-base (CP0)** – [DATA A PREENCHER]
  - Estado inicial preservado; núcleo UCS, DOCS_UCS, GUIA_DO_OPERADOR, PCU, estrutura conceitual organizada.

- **v0.2-ucs-com-dados (CP1)** – [DATA A PREENCHER]
  - UCS ligada a dataset real H(z), ajuste de parâmetros completo, resultados documentados com χ², AIC, BIC.

- **v0.3-guia-educacional (CP2)** – [DATA A PREENCHER]
  - Tutoriais práticos, VISAO_GERAL, GLOSSARIO, FAQ publicados.

- **v0.4-pacote-python (CP3)** – [DATA A PREENCHER]
  - Pacote `pontezafira_ucs` criado, com API básica e empacotamento.

- **v1.0-publico (CP4)** – [DATA A PREENCHER]
  - Repositório pronto para divulgação ampla / submissão de artigo.

---

## 9. Notas finais

### Sobre o escopo científico

A Ponte Zafira **não reivindica nova física confirmada**; ela organiza hipóteses testáveis sob critérios explícitos de coerência e refutabilidade. O modelo UCS-Lagrangiana é um exercício exploratório, não uma alternativa fundamental ao ΛCDM.

### Sobre o Zero / zero-field

O conceito do "zero-field-primordial" pode ser desenvolvido em repositório ou módulo separado, submetido ao mesmo caminho ético da Ponte: sair de visão, passar por hipótese explícita e enfrentar dados, sem proteção especial.

O Zero **não domina** a Ponte; a Ponte **não blinda** o Zero; **os dados decidem ambos**.

---

**Versão:** 1.0  
**Data:** Fevereiro 2026  
**Mantido por:** brunoviniciusdepaularodrigues1-creator  
**Licença:** Ver LICENSE no repositório
