# 🌉 BRIDGE_PROTOCOL — Framework Operacional PCU

## Objetivo
Formalizar os critérios de validade de PCU em forma testável, auditável e aplicável a qualquer domínio.

## 5 Camadas de Análise

### Camada 0: Observação
**Critério:** Dados são públicos, replicáveis, com incerteza declarada.
- Fonte verificável
- Metodologia explícita  
- Erro/incerteza quantificado
- Sem seleção seletiva

### Camada 1: Símbolo
**Critério:** Cada termo tem definição precisa, sem ambiguidade.
- Definição formal (ou referência)
- Diferenciação entre observação e interpretação
- Termos técnicos = documento específico

### Camada 2: Conceito
**Critério:** Nenhuma definição depende de si mesma; encadeamento claro.
- Sem circularidade lógica
- Dependências explícitas (A→B→C)
- Axiomas isolados de derivações

### Camada 3: Formalismo
**Critério:** Equações, modelos, estruturas matemáticas fechadas.
- Derivação completa (não declarativa)
- Variáveis definidas
- Solução ou comportamento descrito

### Camada 4: Interpretação
**Critério:** Conexão entre formalismo e realidade é honesta sobre limites.
- Escopo declarado explicitamente
- Regime de validade (onde falha, por quê)
- Sem extrapolação para domínios não testados

## 8 Tipos de Violação

| Tipo | Descrição | Exemplo |
|------|-----------|----------|
| 1 | Dado confundido com interpretação | "A gravidade não existe" (mistura observação com conclusão) |
| 2 | Símbolo vago ou redefinido | "Energia" sem esclarecimento |
| 3 | Conceito circular | "Verdade é aquilo que é verdadeiro" |
| 4 | Formalismo incompleto | Equação sem solução, parâmetro oculto |
| 5 | Extrapolação além escopo | Cosmologia clássica aplicada a universo primordial |
| 6 | Camadas confundidas | "Campo escalar é real" (mistura modelo com realidade) |
| 7 | Autoridade circular | "PCU é válida porque PCU valida" |
| 8 | Ausência de limites | "Este modelo explica tudo" |

## Checklist de Validação

Antes de submeter qualquer documento a PCU, verifique:

- [ ] **Camada 0:** Dados citados com fonte e incerteza
- [ ] **Camada 1:** Glossário ou referência para cada termo técnico
- [ ] **Camada 2:** Sem definições circulares (teste: inverta dependências)
- [ ] **Camada 3:** Equações derivadas (ou referenciadas com DOI/arxiv)
- [ ] **Camada 4:** Escopo e limitações explícitas em seção dedicada
- [ ] **Verificação:** Nenhuma das 8 violações está presente
- [ ] **Honestidade:** Documento não faz mais afirmações do que prova

## Aplicação a Domínios

Este protocolo é agnóstico a domínio. Aplica-se igualmente a:

- Cosmologia: campo escalar, Hubble(z), data DESI
- Biologia: evolução, mecanismos, dados phylogenéticos
- IA: modelos, treinamento, limites de generalização
- Filosofia: axiomas, derivações, escopo interpretativo

## Validação Automática

Script `PCU/tools/bridge_validator.py` detecta:
- Violações de tipo 1-8 (pattern matching + heurísticas)
- Ausência de termos chave ("limite", "escopo", "validação")
- Circularidade em dependências de conceitos
- Extrapolações sem justificativa

## Integração com UCS-Lagrangiana

Todo documento em `UCS-LAGRANGIANA/` passa por:

1. Leitura contra BRIDGE_PROTOCOL
2. Marcação de violações (ou conformidade)
3. Registro em `data/validation_log.json`

Exemplo:
```json
{
  "document": "UCS-LAGRANGIANA/lagrangiana.md",
  "violations": []
  "score": 1.0,
  "timestamp": "2026-02-05"
}
```

## Próximos Passos

1. Validar `modelo/06_axiomas.md` contra BRIDGE_PROTOCOL
2. Validar `UCS-LAGRANGIANA/lagrangiana.md`
3. Registrar resultados em repositório
4. Usar `bridge_validator.py` em CI/CD (opcional)
