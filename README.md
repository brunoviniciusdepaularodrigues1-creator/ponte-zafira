# Ponte de Zafira

A **Ponte de Zafira** é um projeto conceitual e educacional que integra modelagem simbólica, formalização matemática e experimentação computacional.  
Seu objetivo é explorar **como modelos podem ser construídos, analisados e comparados**, mantendo clareza sobre limites e escopo.

> **Status do projeto:** modelo conceitual em desenvolvimento  
> **Aviso:** este repositório não faz afirmações sobre a realidade física fundamental.  
> ⚠️ **Aviso:** Este projeto é exploratório. Não representa resultados físicos finais.

## 🧱 Organização em Camadas

O projeto Ponte Zafira é estruturado em camadas conceituais independentes, organizadas em uma ordem lógica de construção e leitura:

1. **Intenção, escopo e limites**  
   (README, Manifesto)

2. **Princípios de coerência (PCU)**  
   Camada normativa responsável por definir critérios de consistência, integração e não-contradição entre modelos.

3. **Axiomas conceituais**  
   Base declarativa mínima a partir da qual interpretações podem ser construídas.

4. **Estrutura interpretativa (UCS)**  
   Organização simbólica e conceitual derivada dos axiomas, já avaliada sob os critérios da PCU.

5. **Formalização matemática (UCS-Lagrangiana)**  
   Implementação técnica e exploratória das estruturas interpretativas.

6. **Dados, exemplos e comparações**  
   Uso de dados observacionais e simulações com finalidade exploratória e educacional.

7. **Análise crítica e limitações**  
   Discussão explícita de falhas, limites e escopo do modelo.

As camadas coexistem, mas **não se misturam nem se justificam circularmente**.

---

## 🎯 Escopo do Projeto

O projeto Ponte Zafira possui três componentes complementares, organizados de forma não hierárquica, porém avaliados por critérios claros:

### 1. Eixo Conceitual-Simbólico
- Axiomas
- Manifesto
- Notas reflexivas e críticas
- Estrutura interpretativa (UCS)

### 2. Camada de Coerência (PCU)
- Plataforma de Coerência Universal
- Critérios normativos de consistência
- Separação entre símbolo, modelo e formalismo
- Controle de extrapolações conceituais

### 3. Eixo Técnico-Exploratório
- Modelo cosmológico com campo escalar dinâmico
- Formulação lagrangiana (Φ⁴)
- Equações de campo
- Simulações numéricas
- Comparação com dados cosmológicos H(z)

Os eixos coexistem, mas **não se confundem nem se validam mutuamente**.

---

## 🧩 Estrutura do Repositório

```
ponte-zafira/
├── modelo/              # Documentação conceitual e axiomas
├── UCS-LAGRANGIANA/     # Modelo técnico do campo escalar
│   ├── lagrangiana.md
│   ├── equacoes.md
│   └── nota-cetica.md
├── PCU/                 # Camada conceitual de coerência
│   ├── principios.md
│   ├── arquitetura.md
│   └── exemplos/
├── notas/               # Observações, alertas e comentários
├── data/                # Dados e tabelas cosmológicas
└── README.md
```

---

## 🌌 UCS-Lagrangiana (Resumo Técnico)

O módulo **UCS-Lagrangiana** apresenta um **modelo cosmológico exploratório** baseado em:

- Campo escalar dinâmico Φ
- Potencial quártico:  
  \[
  V(\Phi) = \lambda \Phi^4
  \]
- Evolução cosmológica em função do redshift \( z \)
- Cálculo de:
  - Parâmetro de Hubble \( H(z) \)
  - Equação de estado \( w(z) \)
  - Comparação estatística via \( \chi^2 \)

O modelo é comparado com:
- ΛCDM (como referência)
- Dados observacionais H(z) inspirados em medições do **DESI (DR2)**

---

## 📊 Dados Cosmológicos

O repositório inclui uma tabela comparativa contendo:

- Redshift \( z \)
- H(z) observado
- Incertezas experimentais
- Predições ΛCDM
- Predições do modelo UCS
- Equações de estado
- Valores de \( \chi^2 \)
- Validação observacional exploratória (SN + CC)

Esses dados são usados **exclusivamente para fins educacionais e exploratórios**.

Os dados utilizados estão disponíveis em `data/H_z_data.csv`.

---

## ⚠️ Limitações Declaradas

- O modelo é **efetivo**, não fundamental
- Não há ajuste fino extensivo de parâmetros
- Não se reivindica superioridade sobre ΛCDM
- Instabilidades numéricas são discutidas explicitamente

---

## 📚 Objetivo Educacional

Este projeto serve como:
- exercício de construção de modelos
- treino de formalização matemática
- ponte entre intuição e método científico
- base para evolução futura mais rigorosa

---

## 📎 Navegação Rápida

### 🚀 Comece por aqui
- [📖 Manifesto](manifesto.md)
- [🔍 PCU (Camada de Coerência)](PCU/README.md)

### 🧠 Eixo Conceitual
- [📜 Axiomas](modelo/06_axiomas.md)
- [🔍 Nota Cética UCS](UCS-LAGRANGIANA/nota-cetica.md)

### ⚙️ Eixo Técnico
- [📐 Lagrangiana UCS](UCS-LAGRANGIANA/lagrangiana.md)
- [⚖️ Equações de Campo](UCS-LAGRANGIANA/equacoes.md)

### 📊 Dados
- [📂 Dataset H(z)](data/H_z_data.csv)
- [📄 Documentação de Dados](data/README.md)
