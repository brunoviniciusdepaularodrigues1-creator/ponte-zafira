# Hipótese Científica: Campo Escalar Φ⁴ em Cosmologia FRW

## Estado: Hipótese Nula vs. Alternativa (Testada Numericamente)

Este documento formaliza as hipóteses que guiam a comparação entre o modelo UCS (campo escalar) e o modelo ΛCDM (cosmological constant) usando dados observacionais H(z).

---

## 1. Hipótese Nula (H₀)

**Afirmação:**
```
O modelo UCS (campo escalar Φ⁴ em cosmologia FRW) com
parametrizacao (α, β) arbitrária (não pré-ajustada a z → ∞) 
NÃO produz
 uma função H(z) com ajuste 
às dados observacionais que seja
competível ou superior ao modelo ΛCDM.
```

**Operacionalização:**
```
H₀: χ²_UCS > χ²_ΛCDM  (para o mesmo conjunto de dados)

Ou mais conservador:
H₀: Δχ² = χ²_UCS - χ²_ΛCDM > 0  (com pelo menos p-valor > 0.05)
```

**O que significa:**
- Se H₀ for verdadeira: o modelo UCS não oferece explicação melhor que ΛCDM
- Conclusão: modelo UCS não é competitivo em escala cosmológica
- Implicação: campo escalar é menos viável que constante cosmológica

---

## 2. Hipótese Alternativa (H₁)

**Afirmação:**
```
Existem valores de (α, β) tais que o modelo UCS
(campo escalar Φ⁴ em cosmologia FRW)
produz uma função H(z) com ajuste aos dados
observacionais H(z) (DESI, Pantheon+, CC) que é
competível (ou melhor) que o modelo ΛCDM.
```

**Operacionalização:**
```
H₁: χ²_UCS ≤ χ²_ΛCDM  (ou Δχ² < 0 com significancia)

Ou: existe um conjunto de parâmetros (α, β, Φ₀, Φ'₀)
que minimiza χ²_UCS tal que
χ²_UCS,min / χ²_ΛCDM ≤ κ

onde κ ≈ 1.0 ou ligeiramente < 1.0
```

**O que significa:**
- Se H₁ for verdadeira: o modelo UCS é compatível com dados
- Conclusão: campo escalar é alternativa viável a ΛCDM
- Implicação: teoria efetiva quártica pode descrever expansão acélerada

---

## 3. Sistema de Variáveis e Parâmetros

### 3.1 Parâmetros Livres (a ajustar via MCMC)

| Parâmetro | Intervalo | Significado | Unidades |
|-----------|-----------|------------|----------|
| α | -10 < α < 0 | Coef. quadrático (massa) | [eV²] |
| β | 0 < β < 100 | Acoplamento quártico | adimensional |
| Φ₀ | 0 < Φ₀ < 10 | Campo atual (z=0) | [eV] |
| Φ'₀ | -10 < Φ'₀ < 10 | Derivada atual | [eV²] |

### 3.2 Observáveis Calculados

| Observável | Código | Significado |
|-----------|--------|----------|
| H(z) | Hubble parameter | Parâmetro de Hubble em redshift z |
| w(z) | Equation of state | w = p/ρ (equação de estado) |
| χ² | Chi-squared | Ajuste aos dados |
| AIC | Akaike IC | AIC = 2k + χ² (penalidade k=4) |
| BIC | Bayesian IC | BIC = k ln(n) + χ² (n=número dados) |

---

## 4. Dados Observacionais

### 4.1 Fonte de Dados

**Medições de H(z):**
- **DESI DR2** (Dark Energy Spectroscopic Instrument)
  - Redshift range: 0 < z < 4
  - Método: BAO + clustering
  - Incertezas: ~2-5% em H(z)

- **Cronômetros Cósmicos** (Cosmic Chronometers)
  - Redshift range: 0 < z < 2
  - Método: Δt/Δz de galaxias vermelhas
  - Incertezas: ~3-10% em H(z)

- **Supernovas Pantheon+** (SN Ia)
  - Redshift range: 0 < z < 2.3
  - Métrica: distância luminosa → H(z)
  - Incertezas: ~5-15% em magnitude

### 4.2 Preparação dos Dados

```
Para cada ponto (zᵢ, H_obs(zᵢ), σᵢ):

1. Verificar outliers (> 3σ)
2. Usar covariância Pantheon+ se SN Ia
3. Binning opcional (reduz número de pontos)
4. Normalizar incertezas
```

---

## 5. Procedimento de Teste (MCMC)

### 5.1 Função de Verossimilhança

```
ℒ(dados | α, β, Φ₀, Φ'₀) = 
exp[-χ²(α, β, Φ₀, Φ'₀) / 2]

χ² = Σ [(H_obs(zᵢ) - H_model(zᵢ | α, β, Φ₀, Φ'₀)) / σᵢ]²
```

### 5.2 Prior de Probabilidade

```
Priores uniformes (flat):
- α: [−10, 0]
- β: [0, 100]
- Φ₀: [0, 10]
- Φ'₀: [−10, 10]

Não há prior informado (maximiza espaço paramétrico)
```

### 5.3 Algoritmo: Ensemble MCMC (emcee)

```python
Número de walkers: 32
Número de iterações: 5000
Burn-in: 1000 (primeiras iterações descartadas)
Samples usadas: 4000 × 32 = 128.000 amostras
```

### 5.4 Diagnósticos de Convergência

```
1. Autocorrelation time τ_ac < 100 (sinal de convergência)
2. Gelman-Rubin R̂ < 1.01 (muito próximo de 1)
3. Inspeção visual das cadeias (devem explorar espaço)
4. Teste de mixing (wandering random walk)
```

---

## 6. Critérios de Decisão

### 6.1 Teste χ² Simples

```
Se Δχ² = χ²_UCS - χ²_ΛCDM:

- Δχ² << -10  :  UCS é MUITO preferido (H₁ verdadeira)
- -10 < Δχ² < -2  :  UCS é preferido (suporte a H₁)
- -2 < Δχ² < 2  :  Indistinguível (inconclusivo)
- 2 < Δχ² < 10  :  ΛCDM é preferido (H₀ mantida)
- Δχ² >> 10  :  ΛCDM é MUITO preferido (H₀ confirmada)
```

### 6.2 Teste AIC/BIC (Seleção de Modelo)

```
ΔAIC = AIC_UCS - AIC_ΛCDM

Pontuação AIC (Burnham & Anderson 2002):
- |ΔAIC| < 2  :  evidência substancial para ambos
- 2 < |ΔAIC| < 7  :  suporte moderado para melhor modelo
- |ΔAIC| > 10  :  suporte muito forte para melhor modelo
```

### 6.3 P-valor (Significância Estatística)

```
Usando distribuição χ² com df = n_dados - n_params:

p-valor < 0.05  :  resultado significante (rejeita H₀)
p-valor < 0.01  :  resultado muito significante
p-valor > 0.05  :  resultado não significante (falha em rejeitar H₀)
```

---

## 7. Resultado Esperado

### 7.1 Cenário A: H₁ é Verdadeira (Preferência por UCS)

```
χ²_UCS,min < χ²_ΛCDM
Δχ² < 0 (com |Δχ²| > 2σ)
AIC_UCS < AIC_ΛCDM

Conclusão:
→ Campo escalar Φ⁴ oferece alternativa competitiva
→ Modelo efetivo é viável em escala cosmológica
→ Justifica pesquisa futura com CI melhor ajustadas
```

### 7.2 Cenário B: H₀ é Verdadeira (Preferência por ΛCDM)

```
χ²_UCS,min > χ²_ΛCDM
Δχ² > 0 (com |Δχ²| > 2σ)
AIC_UCS > AIC_ΛCDM

Conclusão:
→ Campo escalar não melhora ajuste observacional
→ Constante cosmológica continua sendo o modelo ótimo
→ Modelo UCS fica confinado a regime educacional/exploratório
```

### 7.3 Cenário C: Indecisão Estatística

```
|Δχ²| < 2
Sobreposição de credible intervals (MCMC)

Conclusão:
→ Ambos modelos são compatíveis com dados
→ Mais dados necessários para decisão
→ Modelo UCS permanece como alternativa viável
```

---

## 8. Independência de Hipóteses

**Crítico:** As hipóteses H₀ e H₁ são:

1. **Mutualmente Exclusivas:**
   - Não podem ser ambas verdadeiras
   - Teste rejeita uma ou a outra (ou inconclusivo)

2. **Exaustivas:**
   - Cobrem todos os cenários relevantes
   - Não há "terceira opção"

3. **Testáveis Numericamente:**
   - χ² é métrica quantitativa
   - MCMC fornece distribuição posterior
   - Decisão é baseada em dados, não opinião

---

## 9. Limitações da Hipótese

1. **Escopo:**
   - Testa apenas em redshift z < 2.5
   - Não aborda regime primordial (BBN, recombinação)
   - Ignora matéria escura fria (CDM)

2. **Modelo:**
   - Campo escalar real (não complexo)
   - Potencial quadrático + quártico (não mais geral)
   - Sem acoplamento a matéria

3. **Dados:**
   - Usa apenas H(z) (não luminosity distance, CMB, BAO separadamente)
   - Cov variância Pantheon+ aproximada
   - Incertezas sistemáticas negligenciadas

4. **Parâmetros:**
   - CI em z=0 são 100% livres (sem restrição de early universe)
   - Sem renormalização QFT (modelo efetivo apenas)

---

## Conclusão

Este documento estabelece um teste rigoroso mas limitado de viabilidade do modelo UCS contra ΛCDM. A decisão entre H₀ e H₁ será determinada puramente por dados observacionais (DESI, Pantheon+) e análise estatística (χ², AIC, MCMC), sem margem para ambiguidade interpretativa.

Ver `derivacao_completa.md` para fundamentos matemáticos e `run_ucs_model.py` para implementação.
