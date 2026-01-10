# Exemplo de raciocínio em PCU (pseudocódigo conceitual)

```
SISTEMA <- definir_componentes()
RELACOES <- mapear_relacoes(SISTEMA)

TENSOES <- []

para cada relacao em RELACOES:
    se relacao for inconsistente:
        adicionar relacao em TENSOES

se tamanho(TENSOES) == 0:
    COERENCIA <- "alta"
senão se tamanho(TENSOES) < limite:
    COERENCIA <- "parcial"
senão:
    COERENCIA <- "baixa"

retornar COERENCIA
```

Este pseudocódigo é ilustrativo e não executável. Ele demonstra apenas a lógica abstrata de leitura da PCU.
