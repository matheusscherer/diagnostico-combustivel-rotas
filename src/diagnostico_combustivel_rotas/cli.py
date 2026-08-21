from __future__ import annotations

import argparse
from pathlib import Path

from diagnostico_combustivel_rotas.analyzer import run_diagnosis
from diagnostico_combustivel_rotas.config import DEFAULT_OUTPUT_DIR, DEFAULT_ROTAS_PATH
from diagnostico_combustivel_rotas.models import RotaPolicy
from diagnostico_combustivel_rotas.report import build_markdown_report, save_reports


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="diagnostico-combustivel-rotas",
        description="Diagnóstico de combustível e rotas.",
    )
    p.add_argument("--rotas", type=Path, default=DEFAULT_ROTAS_PATH)
    p.add_argument("--output", type=Path, default=DEFAULT_OUTPUT_DIR)
    p.add_argument("--desvio-critico", type=float, default=15.0)
    p.add_argument("--no-save", action="store_true")
    return p


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    policy = RotaPolicy(desvio_critico_pct=args.desvio_critico)
    result = run_diagnosis(rotas_path=args.rotas, policy=policy)
    print(build_markdown_report(result))
    if not args.no_save:
        paths = save_reports(result, args.output)
        print("\nArquivos gerados:")
        print(f"  - {paths['markdown']}")
        print(f"  - {paths['excel']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
