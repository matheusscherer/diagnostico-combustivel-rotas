from pathlib import Path

import pandas as pd
import pytest

from diagnostico_combustivel_rotas.loader import load_rotas


def test_referencia_de_distancia_zero_e_rejeitada(data_dir: Path, tmp_path: Path) -> None:
    rotas = pd.read_csv(data_dir / "rotas.csv")
    rotas.loc[0, "km_referencia"] = 0
    caminho = tmp_path / "rotas.csv"
    rotas.to_csv(caminho, index=False)

    with pytest.raises(ValueError, match="km_referencia não pode ser zero"):
        load_rotas(caminho)


def test_arquivo_sem_registros_e_rejeitado(data_dir: Path, tmp_path: Path) -> None:
    rotas = pd.read_csv(data_dir / "rotas.csv").iloc[:0]
    caminho = tmp_path / "rotas_vazias.csv"
    rotas.to_csv(caminho, index=False)

    with pytest.raises(ValueError, match="não contém registros"):
        load_rotas(caminho)
