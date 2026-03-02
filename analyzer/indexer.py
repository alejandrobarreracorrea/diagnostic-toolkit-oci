"""
Data Indexer - Indexación de datos recolectados de OCI.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


class DataIndexer:
    """Indexador de datos recolectados de OCI."""

    def __init__(self, raw_dir: Path, index_dir: Path):
        self.raw_dir = Path(raw_dir)
        self.index_dir = Path(index_dir)
        self.index_dir.mkdir(parents=True, exist_ok=True)

    def index_all(self) -> Dict[str, Any]:
        """Indexar recursos y recomendaciones."""
        index = {
            "compartments": [],
            "tenancy_id": None,
            "resource_types": {},
            "resource_count": 0,
            "recommendations_by_category": defaultdict(list),
            "recommendations_total": 0,
        }

        if not self.raw_dir.exists():
            logger.warning("Directorio raw no existe: %s", self.raw_dir)
            self._save_index(index)
            return index

        meta_file = self.raw_dir / "metadata.json"
        if meta_file.exists():
            try:
                with open(meta_file, "r", encoding="utf-8") as f:
                    meta = json.load(f)
                index["compartments"] = meta.get("compartments", [])
                index["tenancy_id"] = meta.get("tenancy_id")
            except Exception as e:
                logger.warning("Error leyendo metadata: %s", e)

        counts_file = self.raw_dir / "resource_search_counts.json"
        if counts_file.exists():
            try:
                with open(counts_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if data.get("success") and data.get("data"):
                    for row in data["data"]:
                        rtype = row.get("resource_type") or ""
                        cnt = row.get("count", 0)
                        if rtype:
                            index["resource_types"][rtype] = index["resource_types"].get(rtype, 0) + int(cnt)
                    index["resource_count"] = sum(index["resource_types"].values())
            except Exception as e:
                logger.warning("Error leyendo resource_search_counts: %s", e)

        if not index["resource_types"]:
            res_file = self.raw_dir / "resource_search_resources.json"
            if res_file.exists():
                try:
                    with open(res_file, "r", encoding="utf-8") as f:
                        data = json.load(f)
                    for row in data.get("data", []):
                        rtype = row.get("resource_type") or ""
                        if rtype:
                            index["resource_types"][rtype] = index["resource_types"].get(rtype, 0) + 1
                    index["resource_count"] = len(data.get("data", []))
                except Exception as e:
                    logger.warning("Error leyendo resource_search_resources: %s", e)

        opt_file = self.raw_dir / "optimizer_recommendations.json"
        if opt_file.exists():
            try:
                with open(opt_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                for rec in data.get("recommendations", []):
                    cat = rec.get("category") or "other"
                    index["recommendations_by_category"][cat].append(rec)
                    index["recommendations_total"] += 1
            except Exception as e:
                logger.warning("Error leyendo optimizer_recommendations: %s", e)

        index["recommendations_by_category"] = dict(index["recommendations_by_category"])
        self._save_index(index)
        logger.info("Índice generado: %d tipos de recurso, %d recomendaciones", len(index["resource_types"]), index["recommendations_total"])
        return index

    def _save_index(self, index: Dict):
        out = self.index_dir / "index.json"
        with open(out, "w", encoding="utf-8") as f:
            json.dump(index, f, indent=2, default=str)
