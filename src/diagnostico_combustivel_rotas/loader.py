"""Carregamento e validação."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

REQUIRED = [
    "id",
    "data",
    "veiculo",
    "motorista",
    "regiao",
    "km_realizado",
    "km_referencia",
    "litros",
    "preco_litro",
    "entregas",
    "horas_viagem",
    "horas_parado",
    "custo_hora_frota",
]


def load_rotas(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de rotas não encontrado: {path}")

    df = pd.read_csv(path)
    missing = [c for c in REQUIRED if c not in df.columns]
    if missing:
        raise ValueError(f"Colunas obrigatórias ausentes: {missing}")

    df = df.copy()
    df["id"] = df["id"].astype(str).str.strip()
    df["data"] = pd.to_datetime(df["data"], errors="coerce")
    if df["data"].isna().any():
        raise ValueError("Existem datas inválidas")

    for col in ["veiculo", "motorista", "regiao"]:
        df[col] = df[col].astype(str).str.strip()

    nums = [
        "km_realizado",
        "km_referencia",
        "litros",
        "preco_litro",
        "entregas",
        "horas_viagem",
        "horas_parado",
        "custo_hora_frota",
    ]
    for col in nums:
        df[col] = pd.to_numeric(df[col], errors="coerce")
        if df[col].isna().any() or (df[col] < 0).any():
            raise ValueError(f"{col} deve ser numérico e >= 0")

    if (df["km_realizado"] == 0).any():
        raise ValueError("km_realizado não pode ser zero")

    df["km_extras"] = (df["km_realizado"] - df["km_referencia"]).clip(lower=0)
    df["desvio_pct"] = (df["km_extras"] / df["km_referencia"].replace(0, pd.NA) * 100).fillna(0)
    df["custo_combustivel_rs"] = df["litros"] * df["preco_litro"]
    df["custo_por_km"] = df["custo_combustivel_rs"] / df["km_realizado"]
    df["custo_desvio_rs"] = df["km_extras"] * df["custo_por_km"]
    df["custo_ociosidade_rs"] = df["horas_parado"] * df["custo_hora_frota"]
    df["custo_total_desperdicio_rs"] = df["custo_desvio_rs"] + df["custo_ociosidade_rs"]
    df["custo_por_entrega"] = df.apply(
        lambda r: r["custo_combustivel_rs"] / r["entregas"] if r["entregas"] > 0 else 0.0,
        axis=1,
    )
    df["entregas_por_litro"] = df.apply(
        lambda r: r["entregas"] / r["litros"] if r["litros"] > 0 else 0.0,
        axis=1,
    )

    return df.reset_index(drop=True)
