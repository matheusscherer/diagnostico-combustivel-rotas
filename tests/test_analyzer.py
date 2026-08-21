from pathlib import Path

from diagnostico_combustivel_rotas.analyzer import run_diagnosis
from diagnostico_combustivel_rotas.report import build_markdown_report


def test_end_to_end(data_dir: Path) -> None:
    result = run_diagnosis(rotas_path=data_dir / "rotas.csv")
    assert result.summary["km_extras"] == 20.0
    assert result.custo_desvio > 0
    assert "Combustível" in build_markdown_report(result)
