#!/usr/bin/env python3
"""
OCI Diagnostic Collector - Recolección de datos desde Oracle Cloud.

Usa Resource Search para inventario y Optimizer (Cloud Advisor) para recomendaciones.
"""

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Optional

import logging

from .metadata import MetadataCollector
from .resource_search import ResourceSearchCollector
from .optimizer import OptimizerCollector

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def get_config(config_file: Optional[str] = None, profile: Optional[str] = None) -> Dict:
    """Cargar configuración OCI (config file o variables de entorno)."""
    import oci
    profile = profile or os.getenv("OCI_CLI_PROFILE")
    config_file = config_file or os.getenv("OCI_CONFIG_FILE")
    try:
        if config_file:
            return oci.config.from_file(config_file, profile_name=profile)
        return oci.config.from_file(profile_name=profile)
    except Exception as e:
        logger.warning("Error cargando config OCI: %s. Usa ~/.oci/config o OCI_* env vars.", e)
        raise


def get_compartment_ids(compartment_ids: Optional[List[str]] = None, config: Optional[Dict] = None) -> List[str]:
    """Obtener lista de compartment IDs: argumentos > env > todos (tenancy root)."""
    if compartment_ids:
        return compartment_ids
    env = os.getenv("OCI_COMPARTMENT_IDS") or os.getenv("OCI_COMPARTMENT_ID")
    if env:
        return [s.strip() for s in env.split(",")]
    if config:
        return [config["tenancy"]]
    return []


class Collector:
    """Coordinador principal de recolección OCI."""

    def __init__(
        self,
        output_dir: str,
        config: Optional[Dict] = None,
        compartment_ids: Optional[List[str]] = None,
    ):
        self.output_dir = Path(output_dir)
        self.raw_dir = self.output_dir / "raw"
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.config = config or get_config()
        self.compartment_ids = get_compartment_ids(compartment_ids, self.config)
        if not self.compartment_ids:
            self.compartment_ids = [self.config["tenancy"]]
        self.stats = {
            "compartments": len(self.compartment_ids),
            "resources_collected": 0,
            "recommendations_collected": 0,
            "errors": [],
        }

    def collect(self):
        """Ejecutar recolección completa."""
        logger.info("Iniciando recolección OCI")
        logger.info("Compartments: %s", self.compartment_ids[:5] if len(self.compartment_ids) > 5 else self.compartment_ids)

        meta = MetadataCollector(self.config, self.compartment_ids)
        metadata = meta.collect()
        self._save_json("metadata.json", metadata)

        rg = ResourceSearchCollector(self.config, self.compartment_ids)
        resources_result = rg.search_resources()
        if resources_result.get("success"):
            self.stats["resources_collected"] = resources_result.get("total_records", 0) or len(resources_result.get("data", []))
        self._save_json("resource_search_resources.json", resources_result)

        counts_result = rg.collect_counts()
        self._save_json("resource_search_counts.json", counts_result)

        optimizer = OptimizerCollector(self.config, self.compartment_ids)
        opt_result = optimizer.collect_recommendations()
        if opt_result.get("success") is not False:
            self.stats["recommendations_collected"] = opt_result.get("total", 0)
        self._save_json("optimizer_recommendations.json", opt_result)

        logger.info(
            "Recolección completada: %d recursos, %d recomendaciones",
            self.stats["resources_collected"],
            self.stats["recommendations_collected"],
        )
        return self.stats

    def _save_json(self, filename: str, data: Dict):
        path = self.raw_dir / filename
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)


def main():
    parser = argparse.ArgumentParser(description="OCI Diagnostic Collector")
    parser.add_argument("--output-dir", required=True, help="Directorio de salida")
    parser.add_argument("--config", help="Ruta al archivo de config OCI (~/.oci/config)")
    parser.add_argument("--profile", help="Perfil OCI (ej. DEFAULT)")
    parser.add_argument("--compartments", help="IDs de compartment separados por coma")
    args = parser.parse_args()
    config = get_config(config_file=args.config, profile=args.profile)
    compartments = None
    if args.compartments:
        compartments = [s.strip() for s in args.compartments.split(",")]
    collector = Collector(output_dir=args.output_dir, config=config, compartment_ids=compartments)
    collector.collect()
    return 0


if __name__ == "__main__":
    sys.exit(main() or 0)
