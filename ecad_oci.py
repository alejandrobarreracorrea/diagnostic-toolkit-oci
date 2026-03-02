#!/usr/bin/env python3
"""
ECAD OCI - OCI Well-Architected Diagnostic CLI.

Uso:
  python3 ecad_oci.py collect [--run-dir DIR] [--compartments ID1,ID2]
  python3 ecad_oci.py analyze <run_dir>
  python3 ecad_oci.py evidence <run_dir>
  python3 ecad_oci.py reports <run_dir>
  python3 ecad_oci.py full [--run-dir DIR] [--compartments ID1,ID2]
"""

import argparse
import os
import sys
from pathlib import Path
from datetime import datetime


def _run_dir_default():
    return Path("runs") / f"run-{datetime.utcnow().strftime('%Y%m%d-%H%M%S')}"


def _add_common_run_args(parser):
    parser.add_argument("--run-dir", default=None, help="Directorio del run (default: runs/run-YYYYMMDD-HHMMSS)")
    parser.add_argument("--compartments", default=None, help="IDs de compartment separados por coma (default: tenancy root)")
    parser.add_argument("--config", default=None, help="Ruta al archivo de config OCI (default: ~/.oci/config)")
    parser.add_argument("--profile", default=None, help="Perfil OCI (ej. DEFAULT)")


def cmd_collect(args):
    run_dir = Path(args.run_dir) if args.run_dir else _run_dir_default()
    run_dir.mkdir(parents=True, exist_ok=True)
    compartments = [s.strip() for s in args.compartments.split(",")] if args.compartments else None
    from collector.main import Collector, get_config
    config = get_config(config_file=args.config, profile=args.profile)
    c = Collector(str(run_dir), config=config, compartment_ids=compartments)
    c.collect()
    print(f"Run guardado en: {run_dir}")
    return 0


def cmd_analyze(args):
    from analyzer.main import Analyzer
    a = Analyzer(args.run_dir)
    a.analyze()
    return 0


def cmd_evidence(args):
    from evidence.generator import EvidenceGenerator
    g = EvidenceGenerator(args.run_dir)
    g.generate()
    return 0


def cmd_reports(args):
    templates_dir = Path(__file__).resolve().parent / "templates"
    from analyzer.report_generator import ReportGenerator
    gen = ReportGenerator(args.run_dir, templates_dir)
    gen.generate_all()
    return 0


def cmd_full(args):
    run_dir = Path(args.run_dir) if args.run_dir else _run_dir_default()
    run_dir.mkdir(parents=True, exist_ok=True)
    compartments = [s.strip() for s in args.compartments.split(",")] if args.compartments else None
    from collector.main import Collector, get_config
    from analyzer.main import Analyzer
    from evidence.generator import EvidenceGenerator
    from analyzer.report_generator import ReportGenerator
    config = get_config(config_file=getattr(args, "config", None), profile=getattr(args, "profile", None))
    Collector(str(run_dir), config=config, compartment_ids=compartments).collect()
    Analyzer(str(run_dir)).analyze()
    EvidenceGenerator(str(run_dir)).generate()
    ReportGenerator(str(run_dir), Path(__file__).resolve().parent / "templates").generate_all()
    print(f"Diagnóstico completo en: {run_dir}")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="OCI Well-Architected Diagnostic (ECAD OCI)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_collect = sub.add_parser("collect", help="Recolectar datos (Resource Search + Cloud Advisor)")
    _add_common_run_args(p_collect)
    p_collect.set_defaults(func=cmd_collect)

    p_analyze = sub.add_parser("analyze", help="Indexar, inventario y hallazgos")
    p_analyze.add_argument("run_dir", help="Directorio del run")
    p_analyze.set_defaults(func=cmd_analyze)

    p_evidence = sub.add_parser("evidence", help="Generar evidence pack Well-Architected")
    p_evidence.add_argument("run_dir", help="Directorio del run")
    p_evidence.set_defaults(func=cmd_evidence)

    p_reports = sub.add_parser("reports", help="Generar reportes")
    p_reports.add_argument("run_dir", help="Directorio del run")
    p_reports.set_defaults(func=cmd_reports)

    p_full = sub.add_parser("full", help="Ejecutar collect + analyze + evidence + reports")
    _add_common_run_args(p_full)
    p_full.set_defaults(func=cmd_full)

    args = parser.parse_args()
    if getattr(args, "run_dir", None) is None and args.command in ("analyze", "evidence", "reports"):
        parser.error("run_dir requerido para %s" % args.command)
    return args.func(args)


if __name__ == "__main__":
    root = Path(__file__).resolve().parent
    if str(root) not in sys.path:
        sys.path.insert(0, str(root))
    sys.exit(main() or 0)
