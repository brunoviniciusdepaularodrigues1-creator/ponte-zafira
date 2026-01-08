# Ponte de Zafira

A **Ponte de Zafira** é um projeto conceitual e educacional que integra modelagem simbólica, formalização matemática e experimentação computacional.  
Seu objetivo é explorar **como modelos podem ser construídos, analisados e comparados**, mantendo clareza sobre limites e escopo.

> **Status do projeto:** modelo conceitual em desenvolvimento  
> **Aviso:** este repositório não faz afirmações sobre a realidade física fundamental.

---

## 🎯 Escopo do Projeto

O projeto está dividido em dois grandes eixos:

1. **Eixo Conceitual-Simbólico**
   - Axiomas
   - Manifesto
   - Notas reflexivas e críticas
   - Estrutura interpretativa (UCS)

2. **Eixo Técnico-Exploratório**
   - Modelo cosmológico com campo escalar dinâmico
   - Formulação lagrangiana (Φ⁴)
   - Equações de campo
   - Simulações numéricas
   - Comparação com dados cosmológicos H(z)

Os dois eixos coexistem, mas **não se confundem**.

---

## 🧩 Estrutura do Repositório

```
ponte-zafira/
├── modelo/              # Documentação conceitual e axiomas
├── UCS-LAGRANGIANA/     # Modelo técnico do campo escalar
│   ├── lagrangiana.md
│   ├── equacoes.md
│   └── nota-cetica.md
├── notas/               # Observações, alertas e comentários
├── data/                # (em expansão) dados e tabelas cosmológicas
└── README.md
```

---

## 🌌 UCS-Lagrangiana (Resumo Técnico)

O módulo **UCS-Lagrangiana** apresenta um **modelo cosmológico exploratório** baseado em:

- Campo escalar dinâmico Φ
- Potencial quartico:  
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
- Dados observacionais inspirados em medições do **DESI (DR2)**

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

Esses dados são usados **exclusivamente para fins educacionais e exploratórios**.

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

- [📖 Manifesto](manifesto.md)
- [📜 Axiomas](modelo/06_axiomas.md)
- [📐 Lagrangiana UCS](UCS-LAGRANGIANA/lagrangiana.md)
- [⚖️ Equações de Campo](UCS-LAGRANGIANA/equacoes.md)
- [🔍 Nota Cética UCS](UCS-LAGRANGIANA/nota-cetica.md)
