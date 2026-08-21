from __future__ import annotations

from datetime import datetime
from pathlib import Path

from diagnostico_combustivel_rotas.loader import load_rotas
from diagnostico_combustivel_rotas.metrics import compute_summary, rank_by
from diagnostico_combustivel_rotas.models import DiagnosisResult, RotaPolicy


def run_diagnosis(
    rotas_path: Path,
    policy: RotaPolicy | None = None,
) -> DiagnosisResult:
    policy = policy or RotaPolicy()
    rotas = load_rotas(rotas_path)
    summary = compute_summary(rotas, policy)

    notes = [
        "km extras = max(km_realizado − km_referencia, 0).",
        "custo do desvio = km extras × (custo combustível ÷ km realizado).",
        "custo de ociosidade = horas paradas × custo/hora da frota.",
        f"Rota crítica = desvio >= {policy.desvio_critico_pct}% da referência.",
        "Dados de exemplo são sintéticos.",
    ]

    return DiagnosisResult(
        detail=rotas,
        summary=summary,
        by_veiculo=rank_by(rotas, "veiculo"),
        by_motorista=rank_by(rotas, "motorista"),
        by_regiao=rank_by(rotas, "regiao"),
        policy=policy,
        generated_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        notes=notes,
    )
