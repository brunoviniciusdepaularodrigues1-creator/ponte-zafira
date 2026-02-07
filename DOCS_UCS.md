# DOCS_UCS: Documentação do Modelo Cosmológico UCS-Lagrangiana

## 1. Visão Geral

O modelo **UCS-Lagrangiana** é uma proposta exploratória de cosmologia baseada em um **campo escalar dinâmico** com potencial quártico. O objetivo é investigar como um sistema simples de campo pode evoluir e se relacionar com observáveis cosmológicos como o parâmetro de Hubble $H(z)$.

> **Status:** Modelo exploratório, educacional.  
> **Escopo:** Comparar predições com dados de cronométros cósmicos e supernovas Ia.  
> **Limite:** Não se reivindica superioridade sobre $\\Lambda$CDM.  

---

## 2. Formulação Matemática

### 2.1 A Lagrangiana

A ação do campo escalar em FRW é:

$$S = \\int d^4x \\sqrt{-g} \\left[ \\frac{M_p^2}{2} R + \\frac{1}{2} g^{\\mu\\nu} \\partial_\\mu \\Phi \\partial_\\nu \\Phi - V(\\Phi) \\right]$$

onde:
- $M_p$ = massa de Planck reduzida
- $R$ = escalar de curvatura
- $\\Phi$ = campo escalar dinâmico
- $V(\\Phi) = \\lambda \\Phi^4$ = potencial quártico

### 2.2 Equações de Campo

Em FRW ($ds^2 = -dt^2 + a(t)^2 d\\vec{x}^2$), as equações são:

**Equação de Friedmann:**
$$H^2 = \\frac{1}{3M_p^2} \\rho$$

**Aceleração:**
$$\\ddot{a}/a = -\\frac{1}{6M_p^2}(\\rho + 3P)$$

**Densidade e pressão do campo:**
$$\\rho_\\Phi = \\frac{1}{2} \\dot{\\Phi}^2 + V(\\Phi)$$
$$P_\\Phi = \\frac{1}{2} \\dot{\\Phi}^2 - V(\\Phi)$$

**Equação de Klein-Gordon:**
$$\\ddot{\\Phi} + 3H\\dot{\\Phi} + V'(\\Phi) = 0$$

### 2.3 Evolução em Função do Redshift

Utilizando $\\frac{d}{dt} = -H(1+z) \\frac{d}{dz}$, obtemos EDOs acopladas em função de $z$:

$$\\frac{d\\Phi}{dz} = \\frac{\\pi}{H(1+z)}$$
$$\\frac{d\\pi}{dz} = -\\frac{1}{H(1+z)} \\left[ 3\\pi + (1+z) V'(\\Phi) \\right]$$

onde $\\pi = \\dot{\\Phi}$ é o momento canônico.

---

## 3. Dados Observacionais

### 3.1 Conjunto de Dados H(z)

O modelo é testado contra:

- **Cronômetros Cósmicos:** Medidas independentes de $H(z)$ via edade de galáxias vermelhas
- **Supernovas Ia (Pantheon+):** Luminosidades padronizadas em diferentes redshifts
- **Baryon Acoustic Oscillations (BAO):** Oscilações de som cósmico

Fonte de dados: compilação pública (DESI DR2 inspirado)

### 3.2 Limites de Redshift

- **Baixo redshift:** $z \\lesssim 0.1$ (estrutura local)
- **Alto redshift:** $z \\sim 2-3$ (universo jovem)
- **Limites:** Não cobrimos $z > 5$ (era de reionização, requer tratação especial de radiação)

---

## 4. Método de Ajuste

### 4.1 Likelihood e Priors

**Likelihood:** Gaussiana (erros independentes)

$$\\mathcal{L} = \\exp\\left( -\\frac{1}{2} \\sum_i \\left( \\frac{H_i^{obs} - H_i^{mod}}{\\sigma_i} \\right)^2 \\right)$$

**Priors:** Uniformes em faixas físicas razoáveis
- $\\lambda \\in [0.001, 10]$ (constante de acoplamento)
- $\\Phi_0 \\in [0.01, 10] M_p$ (valor inicial do campo)
- $H_0 \\in [60, 80]$ km/s/Mpc (Hubble hoje)

### 4.2 Sampler

- **Método:** Cadeia de Markov Monte Carlo (MCMC) com `emcee` (Ensemble sampler)
- **Terços:** 5000 iterações de burn-in, 10000 produção
- **Diagnósticos:** Autocorrelação, $\\hat{R}$ (fator de condição convergência)

---

## 5. Resultados Esperados

### 5.1 Comparação UCS vs $\\Lambda$CDM

| Métrica | UCS | $\\Lambda$CDM | Status |
|---------|-----|------------|--------|
| $\\chi^2$ | ??? | ??? | A calcular |
| AIC | ??? | ??? | A calcular |
| BIC | ??? | ??? | A calcular |

**Interpretação:**
- Se $\\Delta BIC > 10$ em favor de $\\Lambda$CDM: UCS é disfavorecido
- Se $\\Delta BIC < 2$: Modelos são competitivos
- Se $\\Delta BIC > 10$ em favor de UCS: UCS é preferido

### 5.2 Predições de Superfíieçés

- Evolução de $w(z) = P_\\Phi / \\rho_\\Phi$
- Comparação com WMAP + Planck para parametrizações de $w$
- Validação usando BBN (nucleósíntese do Big Bang)

---

## 6. Limitações e Cuidados

1. **Modelo Efetivo:** Não é derivado de teoria fundamental; é um "toy model" exploratório.

2. **Falta de Radiação:** O modelo não inclui "materia escura" ou radiação explicitly. Estes podem ser inclusos em extensões futuras.

3. **Estabilidade Numérica:** Potenciais muito ump ou muito inclinados podem levar a problemas de integração.

4. **Degenerescências:** Parâmetros $\\lambda$ e $\\Phi_0$ podem ser degenerados na fácie $H(z)$. Dados de CMB podem quebrar essa degenersencia.

5. **Não é "Nova Física":** O UCS não refuta $\\Lambda$CDM. É um exercício de modelagem, não uma alternação fundamental.

---

## 7. Como Usar Este Documento

### Para Físicos/Cosmológos
- Leia as seções 2 (formalismo) e 5 (resultados)
- Refira-se a `UCS-LAGRANGIANA/equacoes.md` para derivacão completa
- Veja `run_ucs_model.py` para implementação numérica

### Para Estudantes
- Começe pela visão geral (seção 1)
- Entenda os dados (seção 3)
- Explore o método de ajuste (seção 4)

### Para Desenvolvedores
- Refira-se a `run_ucs_model.py` para integradores e solvers
- Veja `analise_estatistica.py` para cálculo de $\\chi^2$, AIC, BIC
- É possível adaptar os scripts para outros potenciais ou parametrizações

---

## 8. Referências

1. Dodelson, S. (2003). *Modern Cosmology.* Academic Press.
2. Tsujikawa, S. (2012). Classical scalar field models of dark energy. *J. Phys. Soc. Jpn.*, 76(11), 111015.
3. Liddle, A. R., & Urena-Lopez, L. A. (2006). Inflation, dark energy and dark matter in the scalar-tensor theory of gravitation. *Phys. Rev. D*, 73, 023519.
4. Foreman-Mackey, D., et al. (2013). emcee: The MCMC Hammer. *PASP*, 125(925), 306.
5. DESI Collaboration (2024). Early Results from DESI DR2 (dados em desenvolvimento).

---

**Versão:** 1.0  
**Data:** Fevereiro 2026  
**Mantido por:** bruno...
