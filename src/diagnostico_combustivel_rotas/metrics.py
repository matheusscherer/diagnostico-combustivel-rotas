"""Métricas de impacto financeiro."""

from __future__ import annotations

import pandas as pd

from diagnostico_combustivel_rotas.models import RotaPolicy


def _pct(part: float, whole: float) -> float:
    if whole == 0:
        return 0.0
    return round(100.0 * part / whole, 1)


def compute_summary(rotas: pd.DataFrame, policy: RotaPolicy) -> dict:
    total = len(rotas)
    km_real = float(rotas["km_realizado"].sum())
    km_ref = float(rotas["km_referencia"].sum())
    km_extras = float(rotas["km_extras"].sum())
    litros = float(rotas["litros"].sum())
    entregas = float(rotas["entregas"].sum())

    custo_comb = float(rotas["custo_combustivel_rs"].sum())
    custo_desvio = float(rotas["custo_desvio_rs"].sum())
    custo_ocio = float(rotas["custo_ociosidade_rs"].sum())

    criticas = int((rotas["desvio_pct"] >= policy.desvio_critico_pct).sum())

    return {
        "periodo_inicio": rotas["data"].min().strftime("%Y-%m-%d"),
        "periodo_fim": rotas["data"].max().strftime("%Y-%m-%d"),
        "total_rotas": total,
        "rotas_criticas": criticas,
        "pct_rotas_criticas": _pct(criticas, total),
        "km_realizado": round(km_real, 1),
        "km_referencia": round(km_ref, 1),
        "km_extras": round(km_extras, 1),
        "desvio_pct": _pct(km_extras, km_ref),
        "litros": round(litros, 1),
        "entregas": int(entregas),
        "custo_combustivel_rs": round(custo_comb, 2),
        "custo_desvio_rs": round(custo_desvio, 2),
        "custo_ociosidade_rs": round(custo_ocio, 2),
        "impacto_total_rs": round(custo_desvio + custo_ocio, 2),
        "custo_medio_por_entrega": round(custo_comb / entregas, 2) if entregas else 0.0,
        "desvio_critico_pct": policy.desvio_critico_pct,
    }


def rank_by(rotas: pd.DataFrame, group_col: str) -> pd.DataFrame:
    if rotas.empty:
        return pd.DataFrame()

    g = (
        rotas.groupby(group_col, as_index=False)
        .agg(
            rotas=("id", "count"),
            km_extras=("km_extras", "sum"),
            litros=("litros", "sum"),
            entregas=("entregas", "sum"),
            custo_desvio_rs=("custo_desvio_rs", "sum"),
            custo_ociosidade_rs=("custo_ociosidade_rs", "sum"),
            custo_total_desperdicio_rs=("custo_total_desperdicio_rs", "sum"),
            custo_combustivel_rs=("custo_combustivel_rs", "sum"),
        )
    )
    g["custo_por_entrega"] = g.apply(
        lambda r: r["custo_combustivel_rs"] / r["entregas"] if r["entregas"] > 0 else 0.0,
        axis=1,
    )
    return g.sort_values(
        by=["custo_total_desperdicio_rs", "km_extras"], ascending=False
    ).reset_index(drop=True)
