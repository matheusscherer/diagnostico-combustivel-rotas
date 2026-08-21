from __future__ import annotations

from pathlib import Path
from typing import Union

import pandas as pd

from diagnostico_combustivel_rotas.models import DiagnosisResult

PathLike = Union[str, Path]


def _fmt_brl(v: float) -> str:
    return f"R$ {v:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _fmt_num(v: float, d: int = 1) -> str:
    return f"{v:,.{d}f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _rank(df: pd.DataFrame, key: str, lines: list[str], limit: int = 10) -> None:
    if df.empty:
        lines.append("_Sem dados._")
        return
    lines.append(
        f"| {key.capitalize()} | Rotas | Km extras | Entregas | Custo desvio | Ociosidade | Total |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")
    for _, r in df.head(limit).iterrows():
        lines.append(
            f"| {r[key]} | {int(r['rotas'])} | {_fmt_num(r['km_extras'])} | {int(r['entregas'])} | "
            f"{_fmt_brl(r['custo_desvio_rs'])} | {_fmt_brl(r['custo_ociosidade_rs'])} | "
            f"{_fmt_brl(r['custo_total_desperdicio_rs'])} |"
        )


def build_markdown_report(result: DiagnosisResult) -> str:
    s = result.summary
    lines = [
        "# Diagnóstico de Combustível e Rotas",
        "",
        f"**Período:** {s['periodo_inicio']} a {s['periodo_fim']}",
        f"**Gerado em:** {result.generated_at}",
        "",
        "> Objetivo: quantificar **km extras**, **combustível desperdiçado** e **frota ociosa**.",
        "",
        "---",
        "",
        "## Resumo executivo",
        "",
        "| Métrica | Valor |",
        "|---------|-------|",
        f"| Rotas analisadas | {s['total_rotas']} |",
        f"| Rotas críticas (desvio ≥ {s['desvio_critico_pct']}%) | {s['rotas_criticas']} ({s['pct_rotas_criticas']}%) |",
        f"| Km realizados | {_fmt_num(s['km_realizado'])} |",
        f"| Km de referência | {_fmt_num(s['km_referencia'])} |",
        f"| **Km extras** | **{_fmt_num(s['km_extras'])}** ({s['desvio_pct']}%) |",
        f"| Litros consumidos | {_fmt_num(s['litros'])} |",
        f"| Entregas | {s['entregas']} |",
        f"| Custo combustível | {_fmt_brl(s['custo_combustivel_rs'])} |",
        f"| Custo médio por entrega | {_fmt_brl(s['custo_medio_por_entrega'])} |",
        f"| **Custo do desvio** | **{_fmt_brl(s['custo_desvio_rs'])}** |",
        f"| **Custo de ociosidade** | **{_fmt_brl(s['custo_ociosidade_rs'])}** |",
        f"| **Impacto total** | **{_fmt_brl(s['impacto_total_rs'])}** |",
        "",
        "---",
        "",
        "## Por veículo",
        "",
    ]
    _rank(result.by_veiculo, "veiculo", lines)
    lines.extend(["", "---", "", "## Por motorista", ""])
    _rank(result.by_motorista, "motorista", lines)
    lines.extend(["", "---", "", "## Por região", ""])
    _rank(result.by_regiao, "regiao", lines)

    lines.extend(["", "---", "", "## Premissas", ""])
    for n in result.notes:
        lines.append(f"- {n}")

    lines.extend(
        [
            "",
            "---",
            "",
            "## Próximas ações sugeridas",
            "",
            "1. Revisar as rotas com maior **custo de desvio** (não só km).",
            "2. Investigar veículos/motoristas com ociosidade recorrente.",
            "3. Recalcular referência de km nas regiões com desvio estrutural.",
            "4. Acompanhar custo por entrega ciclo a ciclo.",
            "",
        ]
    )
    return "\n".join(lines)


def save_reports(
    result: DiagnosisResult,
    output_dir: PathLike,
    prefix: str = "diagnostico_combustivel_rotas",
) -> dict:
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{prefix}.md"
    xlsx_path = output_dir / f"{prefix}.xlsx"
    md_path.write_text(build_markdown_report(result), encoding="utf-8")
    with pd.ExcelWriter(xlsx_path, engine="openpyxl") as w:
        result.detail.to_excel(w, sheet_name="detalhe", index=False)
        result.by_veiculo.to_excel(w, sheet_name="por_veiculo", index=False)
        result.by_motorista.to_excel(w, sheet_name="por_motorista", index=False)
        result.by_regiao.to_excel(w, sheet_name="por_regiao", index=False)
        pd.DataFrame([result.summary]).to_excel(w, sheet_name="resumo", index=False)
    return {"markdown": str(md_path), "excel": str(xlsx_path)}
