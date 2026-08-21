from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def data_dir(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    raw.mkdir()
    pd.DataFrame(
        [
            {
                "id": "R1",
                "data": "2026-08-01",
                "veiculo": "V1",
                "motorista": "A",
                "regiao": "Norte",
                "km_realizado": 120,
                "km_referencia": 100,
                "litros": 20,
                "preco_litro": 6.0,
                "entregas": 10,
                "horas_viagem": 5,
                "horas_parado": 1,
                "custo_hora_frota": 50,
            }
        ]
    ).to_csv(raw / "rotas.csv", index=False)
    return raw
