from pathlib import Path

from diagnostico_combustivel_rotas.history import list_recent_runs, save_run


def test_historico_salva_apenas_resumo_e_retorna_execucao(tmp_path: Path) -> None:
    db_path = tmp_path / "nested" / "history.sqlite3"
    summary = {
        "desvio_critico_pct": 15.0,
        "total_rotas": 4,
        "km_extras": 20.0,
        "impacto_total_rs": 120.5,
    }

    run_id = save_run(db_path, summary)
    runs = list_recent_runs(db_path)

    assert run_id == 1
    assert len(runs) == 1
    assert runs[0]["summary"] == summary
    assert runs[0]["critical_deviation_pct"] == 15.0
    assert list_recent_runs(tmp_path / "missing.sqlite3") == []
