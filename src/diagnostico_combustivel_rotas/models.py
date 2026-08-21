from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class RotaPolicy:
    """Parâmetros do diagnóstico."""

    # Desvio percentual acima do qual a rota é marcada como crítica
    desvio_critico_pct: float = 15.0

    def __post_init__(self) -> None:
        if self.desvio_critico_pct < 0:
            raise ValueError("desvio_critico_pct deve ser >= 0")


@dataclass
class DiagnosisResult:
    detail: pd.DataFrame
    summary: dict
    by_veiculo: pd.DataFrame
    by_motorista: pd.DataFrame
    by_regiao: pd.DataFrame
    policy: RotaPolicy
    generated_at: str
    notes: list[str] = field(default_factory=list)

    @property
    def custo_desvio(self) -> float:
        return float(self.summary.get("custo_desvio_rs", 0.0))

    @property
    def custo_ociosidade(self) -> float:
        return float(self.summary.get("custo_ociosidade_rs", 0.0))

    @property
    def impacto_total(self) -> float:
        return self.custo_desvio + self.custo_ociosidade
