from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory

import streamlit as st

from diagnostico_combustivel_rotas.analyzer import run_diagnosis
from diagnostico_combustivel_rotas.config import (
    DEFAULT_HISTORY_DB,
    DEFAULT_ROTAS_PATH,
)
from diagnostico_combustivel_rotas.history import list_recent_runs, save_run
from diagnostico_combustivel_rotas.models import RotaPolicy
from diagnostico_combustivel_rotas.report import build_markdown_report, save_reports


def _format_number(value: float, decimals: int = 1) -> str:
    formatted = f"{value:,.{decimals}f}"
    return formatted.replace(",", "X").replace(".", ",").replace("X", ".")


def _format_brl(value: float) -> str:
    return f"R$ {_format_number(value, 2)}"


st.set_page_config(page_title="Diagnóstico de Rotas", layout="wide")
st.title("Diagnóstico de combustível e rotas")
st.caption(
    "Dados enviados são processados durante a análise. O histórico salva apenas "
    "resumos; não grava o CSV original."
)

origem = st.radio(
    "Fonte dos dados",
    ["Exemplo sintético", "Carregar CSV"],
    horizontal=True,
)
arquivo = None
if origem == "Carregar CSV":
    arquivo = st.file_uploader("Selecione o arquivo de rotas", type=["csv"])
    st.caption(
        "CSV de até 10 MB. Colunas obrigatórias: "
        "id, data, veiculo, motorista, regiao, km_realizado, km_referencia, "
        "litros, preco_litro, entregas, horas_viagem, horas_parado, "
        "custo_hora_frota."
    )

desvio_critico = st.number_input(
    "Desvio crítico (%)",
    min_value=0.0,
    max_value=100.0,
    value=15.0,
    step=0.5,
)

if st.button(
    "Analisar rotas",
    type="primary",
    disabled=origem == "Carregar CSV" and arquivo is None,
):
    st.session_state.pop("analysis", None)
    try:
        with TemporaryDirectory() as temp_dir:
            caminho_entrada = Path(temp_dir) / "rotas.csv"
            if origem == "Exemplo sintético":
                caminho_entrada.write_bytes(DEFAULT_ROTAS_PATH.read_bytes())
            elif arquivo is None:
                raise ValueError("Selecione um arquivo CSV para continuar")
            else:
                caminho_entrada.write_bytes(arquivo.getvalue())

            resultado = run_diagnosis(
                caminho_entrada,
                policy=RotaPolicy(desvio_critico_pct=desvio_critico),
            )
            relatorio_md = build_markdown_report(resultado)
            arquivos = save_reports(resultado, Path(temp_dir) / "relatorios")
            planilha = Path(arquivos["excel"]).read_bytes()
            run_id = save_run(DEFAULT_HISTORY_DB, resultado.summary)

        st.session_state["analysis"] = {
            "result": resultado,
            "markdown": relatorio_md,
            "excel": planilha,
            "run_id": run_id,
        }
    except (FileNotFoundError, ValueError) as exc:
        st.error(f"Não foi possível analisar o CSV: {exc}")

analysis = st.session_state.get("analysis")
if analysis:
    result = analysis["result"]
    summary = result.summary
    st.success(f"Análise #{analysis['run_id']} concluída.")

    columns = st.columns(4)
    columns[0].metric("Rotas", summary["total_rotas"])
    columns[1].metric("Km extras", f"{_format_number(summary['km_extras'])} km")
    columns[2].metric(
        "Rotas críticas",
        f"{_format_number(summary['pct_rotas_criticas'])}%",
    )
    columns[3].metric("Impacto estimado", _format_brl(summary["impacto_total_rs"]))

    st.subheader("Impacto por região")
    regional = result.by_regiao.set_index("regiao")[
        ["custo_total_desperdicio_rs"]
    ].rename(columns={"custo_total_desperdicio_rs": "Impacto estimado (R$)"})
    st.bar_chart(regional)

    st.subheader("Detalhamento por veículo")
    ranking = result.by_veiculo.rename(
        columns={
            "veiculo": "Veículo",
            "rotas": "Rotas",
            "km_extras": "Km extras",
            "litros": "Litros",
            "entregas": "Entregas",
            "custo_desvio_rs": "Custo do desvio",
            "custo_ociosidade_rs": "Custo da ociosidade",
            "custo_total_desperdicio_rs": "Impacto estimado",
            "custo_combustivel_rs": "Custo combustível",
            "custo_por_entrega": "Custo por entrega",
        }
    )
    for column in (
        "Custo do desvio",
        "Custo da ociosidade",
        "Impacto estimado",
        "Custo combustível",
        "Custo por entrega",
    ):
        ranking[column] = ranking[column].map(_format_brl)
    ranking["Km extras"] = ranking["Km extras"].map(_format_number)
    st.dataframe(ranking, width="stretch", hide_index=True)

    download_columns = st.columns(2)
    download_columns[0].download_button(
        "Baixar relatório Markdown",
        data=analysis["markdown"],
        file_name="diagnostico_combustivel_rotas.md",
        mime="text/markdown",
    )
    download_columns[1].download_button(
        "Baixar planilha Excel",
        data=analysis["excel"],
        file_name="diagnostico_combustivel_rotas.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

st.subheader("Histórico recente")
historico = list_recent_runs(DEFAULT_HISTORY_DB)
if historico:
    st.dataframe(
        [
            {
                "Execução": run["id"],
                "Data (UTC)": run["created_at"],
                "Rotas": run["summary"]["total_rotas"],
                "Km extras": _format_number(run["summary"]["km_extras"]),
                "Impacto estimado": _format_brl(
                    run["summary"]["impacto_total_rs"]
                ),
                "Limite crítico": (
                    f"{_format_number(run['critical_deviation_pct'])}%"
                ),
            }
            for run in historico
        ],
        width="stretch",
        hide_index=True,
    )
else:
    st.info("Ainda não há análises salvas.")
