# Diagnóstico de Combustível e Rotas

<p align="left">
  <img src="https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python" />
  <img src="https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white" alt="Pandas" />
  <img src="https://img.shields.io/badge/pytest-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="pytest" />
  <img src="https://img.shields.io/badge/GitHub_Actions-2088FF?style=for-the-badge&logo=githubactions&logoColor=white" alt="GitHub Actions" />
  <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="MIT" />
</p>

**Problema de negócio:** a frota roda mais do que o necessário e fica parada sem entregar.  
Combustível e tempo viram desperdício.

Este projeto transforma a planilha de rotas em um diagnóstico objetivo:

- **Km extras** vs rota de referência
- **Custo do desvio** em R$
- **Ociosidade** da frota
- Concentração por veículo, motorista e região

> Feito para ser lido por gestor e executado por analista.

---

## Como rodar

```bash
git clone https://github.com/matheusscherer/diagnostico-combustivel-rotas.git
cd diagnostico-combustivel-rotas
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
python -m diagnostico_combustivel_rotas
pytest -v
```

---

## Formato

```text
id,data,veiculo,motorista,regiao,km_realizado,km_referencia,litros,preco_litro,entregas,horas_viagem,horas_parado,custo_hora_frota
R-001,2026-08-15,ABC1A11,Carlos,Norte,120,100,18.5,6.20,12,5.0,0.8,55
```

---

## Lógica

1. km extras = max(realizado − referência, 0)
2. custo combustível = litros × preço/litro
3. custo do desvio = km extras × (custo combustível ÷ km realizado)
4. custo ociosidade = horas paradas × custo/hora da frota
5. rota crítica = desvio ≥ 15% (configurável)

---

## Autor

**Matheus Scherer** · Porto Alegre, RS  
[GitHub](https://github.com/matheusscherer) · [LinkedIn](https://linkedin.com/in/scherermatheus) · [Site](https://mtsch.vercel.app)
