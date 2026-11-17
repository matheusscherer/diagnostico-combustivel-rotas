# Dados de entrada

## rotas.csv

Cada linha = uma rota / viagem executada.

| Coluna | Tipo | Descrição |
|--------|------|-----------|
| id | texto | Identificador da rota |
| data | data (YYYY-MM-DD) | Data da viagem |
| veiculo | texto | Placa ou código do veículo |
| motorista | texto | Nome do motorista |
| regiao | texto | Região / centro de custo |
| km_realizado | número | Km efetivamente rodados |
| km_referencia | número > 0 | Km da rota planejada / ótima; zero é inválido porque impede calcular o desvio percentual |
| litros | número | Combustível consumido (L) |
| preco_litro | número | Preço do litro (R$) |
| entregas | número | Quantidade de entregas na rota |
| horas_viagem | número | Horas totais da viagem |
| horas_parado | número | Horas paradas / ociosas na viagem |
| custo_hora_frota | número | Custo/hora da frota parada (motorista + veículo) |

## Lógica

- **km extras** = max(km_realizado − km_referencia, 0)
- **custo combustível** = litros × preco_litro
- **custo do desvio** = km extras × (custo combustível ÷ km_realizado)
- **custo ociosidade** = horas_parado × custo_hora_frota
