# Derivação Completa: Campo Escalar UCS em Cosmologia FRW

## Status: Modelo Exploratório Efetivo (não fundamental)

Este documento deriva as equações de movimento do campo escalar Φ⁴ em espaço-tempo cosmológico de Friedmann-Robertson-Walker (FRW), conectando a Lagrangiana ao comportamento observável H(z).

---

## SEÇÃO 1: Ação Total e Lagrangiana

### 1.1 Métrica FRW

```
ds² = -dt² + a(t)² [dr² + r²(dθ² + sin²θ dφ²)]
```

Ou em termos de redshift z = 1/a - 1:
- a(t) = 1/(1+z)
- H(z) = da/dt / a = -(1+z) dz/dt

### 1.2 Ação Einstein-Hilbert com Campo Escalar

```
S = ∫ d⁴x √-g [R/(16πG) + ℒ_Φ] + S_m
```

Onde:
- R = escalar de Ricci
- G = constante de Newton
- ℒ_Φ = Lagrangiana do campo escalar
- S_m = ação de matéria (desprezada aqui)

### 1.3 Lagrangiana do Campo Escalar

```
ℒ_Φ = (1/2) g^μν ∂_μ Φ ∂_ν Φ - V(Φ)

V(Φ) = (α/2) Φ² + (β/4) Φ⁴
```

Parâmetros físicos (não simbólicos nesta seção):
- α: Coeficiente de massa quadrática (α < 0 para potencial limitado inferiormente)
- β > 0: Acoplamento quártico (adimensional em unidades naturais)
- Φ: Campo escalar real (unidades de energia/massa)

---

## SEÇÃO 2: Equações de Campo (Variação Funcional)

### 2.1 Equações de Einstein

Variando a ação com respeito à métrica g_μν:

```
G_μν = 8πG T_μν^Φ

onde G_μν = R_μν - (1/2) g_μν R  (tensor de Einstein)
```

### 2.2 Tensor Energia-Momento do Campo

Variando a ação com respeito a ℒ_Φ:

```
T_μν^Φ = ∂_μ Φ ∂_ν Φ - g_μν [(1/2) g^ρσ ∂_ρ Φ ∂_σ Φ - V(Φ)]
```

Em FRW com Φ = Φ(t) homogêneo:
- Densidade de energia: ρ_Φ = (1/2) Φ̇² + V(Φ)
- Pressão: p_Φ = (1/2) Φ̇² - V(Φ)

### 2.3 Equação de Klein-Gordon em FRW

Variando a ação com respeito a Φ:

```
∂_μ (√-g g^μν ∂_ν Φ) - √-g ∂V/∂Φ = 0
```

Em FRW (com a(t) homogêneo):

```
Φ̈ + 3H Φ̇ + ∂V/∂Φ = 0

onde:
- Φ̈ = d²Φ/dt²
- Φ̇ = dΦ/dt  
- H = (1/a) da/dt = parâmetro de Hubble
- ∂V/∂Φ = α Φ + β Φ³
```

**Equação de movimento do campo escalar:**
```
Φ̈ + 3H Φ̇ + α Φ + β Φ³ = 0
```

---

## SEÇÃO 3: Equações de Friedmann Modificadas

### 3.1 Equações 0-0 e i-i de Einstein

A métrica FRW implica:

```
G_00 = -3(H² + Ḧ/H)     [componente temporal]
G_ii = (H² + 2Ḧ/H)       [componentes espaciais]
```

Substituindo T_μν^Φ:

```
H² = (8πG/3) ρ_Φ = (8πG/3) [(1/2) Φ̇² + V(Φ)]

Ḧ = -(4πG) [ρ_Φ + p_Φ] = -(4πG) [Φ̇²]
```

### 3.2 Primeira Equação de Friedmann

```
H² = (8πG/3) [(1/2) Φ̇² + (α/2) Φ² + (β/4) Φ⁴]
```

Em unidades onde 8πG = 1 (unidades naturais):

```
H² = (1/3) [(1/2) Φ̇² + (α/2) Φ² + (β/4) Φ⁴]
```

### 3.3 Equação de Continuidade

```
dρ/dt + 3H(ρ + p) = 0

ou equivalentemente:

ρ̇_Φ = -3H (ρ_Φ + p_Φ) = -3H Φ̇²
```

Esta equação é automaticamente satisfeita pelos Friedmann + Klein-Gordon.

---

## SEÇÃO 4: Conversão para Redshift z

### 4.1 Mudança de Variável: Tempo → Redshift

Relação cosmológica:
```
z = 1/a - 1  →  a = 1/(1+z)

da/dt = -a² H  →  dz/dt = -(1+z) H
```

Derivada temporal em relação a z:
```
d/dt = (dz/dt)^(-1) d/dz = -1/[H(1+z)] d/dz

derivada segunda:
d²/dt² = 1/[H²(1+z)²] d²/dz² + [dH/dz · 1/(H(1+z)) + 1/(1+z)²] d/dz
```

### 4.2 Equação de Klein-Gordon em z

Substituindo Φ̇ = -Φ'/[H(1+z)] e Φ̈ em termos de derivadas em z:

```
Φ'' + [H'/H² + 3/(1+z)] Φ' + [1 + H'/(H²(1+z)²)] [α Φ + β Φ³] = 0

onde Φ' = dΦ/dz
```

### 4.3 Primeira Equação de Friedmann em z

```
H² = (1/3) [(1/2) (Φ'/[H(1+z)])² + (α/2) Φ² + (β/4) Φ⁴]

resolvendo para H²:

H²(1+z)² = (1/2) Φ'² + [(α/2) Φ² + (β/4) Φ⁴] (1+z)²
```

Esta é a **relação chave** que conecta H(z) ao campo Φ(z).

---

## SEÇÃO 5: Solução Numérica e H(z)

### 5.1 Sistema de ODEs

Para computação, convertemos para um sistema de primeira ordem:

```
dΦ/dz = Y

dY/dz = -[H'/H² + 3/(1+z)] Y - [1 + H'/(H²(1+z)²)] [α Φ + β Φ³]

H(z) = √{(1/3) [(1/2) (Y/[H(1+z)])² + (α/2) Φ² + (β/4) Φ⁴]} · (1+z)
```

Mas H aparece em ambos os lados. Solução:

```
H²(1+z)² = (1/2) Y² + [(α/2) Φ² + (β/4) Φ⁴] (1+z)²

H(z) = √{[(1/2) Y² + [(α/2) Φ² + (β/4) Φ⁴] (1+z)²] / (1+z)²}
```

### 5.2 Condições Iniciais

No redshift alto (z → ∞, época antiga):
- Campo dominado por energia de repouso ou radiação
- Ou especificar em z = 0 (presente)

Escolhemos CI em z = 0:
```
Φ(0) = Φ₀     (valor atual do campo)
Φ'(0) = Y₀     (derivada atual)
```

### 5.3 Equação de Estado

Equação de estado efetiva:
```
w(z) = p_Φ / ρ_Φ = [(1/2)(Φ'/[H(1+z)])² - V(Φ)] / [(1/2)(Φ'/[H(1+z)])² + V(Φ)]
```

Se w < -1/3: expansão acelerada (semelhante a dark energy)  
Se w ≈ 0: matéria (kinetic-dominated)  
Se w → -1: cosmological constant

### 5.4 Método Numérico (Runge-Kutta 4ª ordem)

```python
# Pseudocódigo
for i in range(len(z)):
    H[i] = compute_H(Φ[i], Y[i], z[i])
    dΦ = Y[i]
    dY = -[...] Y - [...]  # coefficientes acima
    
    Φ[i+1] = Φ[i] + Δz * RK4(...)
    Y[i+1] = Y[i] + Δz * RK4(...)
```

---

## SEÇÃO 6: Observáveis e Comparação

### 6.1 Parâmetro de Hubble Observado

O output numérico produz H(z) que pode ser comparado com dados observacionais:
- DESI DR2 (Hubble Space Telescope, BAO, etc.)
- Supernovas Pantheon+
- Cronômetros Cósmicos

### 6.2 Teste Estatístico

```
χ² = Σ [(H_obs(zᵢ) - H_model(zᵢ)) / σᵢ]²
```

Onde σᵢ = incerteza experimental em H(zᵢ)

Comparar:
- χ²_UCS (modelo presente)
- χ²_ΛCDM (modelo referência)
- Δχ² = χ²_UCS - χ²_ΛCDM

Se Δχ² << 0: modelo UCS é preferido  
Se Δχ² >> 0: modelo ΛCDM é preferido

---

## Resumo da Derivação

| Passo | Equação | Referência |
|-------|---------|------------|
| 1 | ℒ = (1/2)∂²Φ - V(Φ) | Lagrangiana |
| 2 | Φ̈ + 3H Φ̇ + ∂V/∂Φ = 0 | Klein-Gordon |
| 3 | H² = (8πG/3) [ρ_Φ] | Friedmann |
| 4 | Conversão para z | Cosmografia |
| 5 | Sistema ODE + RK4 | Integração numérica |
| 6 | χ² com dados | Validação observacional |

---

## Observação Crítica

Esta derivação assume:
- Campo escalar como **única componente dinâmica** (negligencia matéria escura, bariônica)
- Modelo **efetivo** válido em z < 2 (não pretende descrever recombinação ou BBN)
- Parâmetros α, β **ajustados** para reproduzir dados (regressão, MCMC)
- Sem renormalização: válido apenas em escala cosmológica clássica

Ver `nota-cetica.md` para limitações explícitas.
