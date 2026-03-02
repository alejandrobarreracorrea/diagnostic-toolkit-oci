#!/usr/bin/env python3
"""
Evidence Pack Generator - Evidencias para OCI Well-Architected Review.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

from evidence import WELL_ARCH_VERSION, WELL_ARCH_DOC_URL

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PILLARS = [
    "Operational Excellence",
    "Security",
    "Reliability",
    "Cost Optimization",
    "Performance Efficiency",
    "Sustainability",
]

CATEGORY_TO_PILLAR = {
    "cost_optimization": "Cost Optimization",
    "performance": "Performance Efficiency",
    "high_availability": "Reliability",
    "security": "Security",
    "operational_excellence": "Operational Excellence",
    "all": "Operational Excellence",
}


class EvidenceGenerator:
    """Generador de evidence pack para OCI Well-Architected."""

    def __init__(self, run_dir: str):
        self.run_dir = Path(run_dir)
        self.raw_dir = self.run_dir / "raw"
        self.index_dir = self.run_dir / "index"
        self.output_dir = self.run_dir / "outputs" / "evidence"
        self.output_dir.mkdir(parents=True, exist_ok=True)

        questions_file = Path(__file__).parent / "well_architected_questions_oci.json"
        mapping_file = Path(__file__).parent / "question_resource_mapping.json"
        self.well_architected_questions = {}
        self.question_resource_mapping = {}
        if questions_file.exists():
            with open(questions_file, "r", encoding="utf-8") as f:
                self.well_architected_questions = json.load(f)
        if mapping_file.exists():
            with open(mapping_file, "r", encoding="utf-8") as f:
                self.question_resource_mapping = json.load(f)

    def generate(self):
        """Generar evidence pack completo."""
        logger.info("Generando evidence pack para OCI Well-Architected")
        index_file = self.index_dir / "index.json"
        if not index_file.exists():
            logger.error("Índice no encontrado: %s", index_file)
            return

        with open(index_file, "r", encoding="utf-8") as f:
            index = json.load(f)

        evidence_pack = {
            "metadata": {
                "run_dir": str(self.run_dir),
                "generated_at": datetime.utcnow().isoformat(),
                "compartments": index.get("compartments", []),
                "tenancy_id": index.get("tenancy_id"),
                "well_arch_version": WELL_ARCH_VERSION,
                "well_arch_url": WELL_ARCH_DOC_URL,
            },
            "pillars": {},
        }

        for pillar in PILLARS:
            logger.info("Generando evidencias para: %s", pillar)
            evidence_pack["pillars"][pillar] = self._generate_pillar_evidence(pillar, index)

        out_file = self.output_dir / "evidence_pack.json"
        with open(out_file, "w", encoding="utf-8") as f:
            json.dump(evidence_pack, f, indent=2, default=str)
        logger.info("Evidence pack guardado en: %s", out_file)

    def _generate_pillar_evidence(self, pillar: str, index: Dict) -> Dict:
        """Generar evidencias para un pilar."""
        pillar_key = pillar.lower().replace(" ", "_")

        evidence = []
        resource_types = index.get("resource_types", {})

        mapping = self.question_resource_mapping.get(pillar_key, {})
        for qid, qmap in mapping.items():
            for rtype in qmap.get("resource_types", []):
                count = resource_types.get(rtype, 0)
                if count > 0:
                    evidence.append({
                        "category": "resource",
                        "resource_type": rtype,
                        "count": count,
                        "question_id": qid,
                    })

        recs_by_cat = index.get("recommendations_by_category", {})
        for cat_key, pillar_name in CATEGORY_TO_PILLAR.items():
            if pillar_name != pillar:
                continue
            recs = recs_by_cat.get(cat_key, [])
            for rec in recs[:50]:
                evidence.append({
                    "category": "optimizer",
                    "importance": rec.get("importance"),
                    "description": rec.get("description"),
                    "recommendation_id": rec.get("id"),
                })

        questions_config = self.well_architected_questions.get(pillar_key, {})
        well_arch_questions = []
        for qid, qdata in questions_config.items():
            related_types = (mapping.get(qid) or {}).get("resource_types", [])
            has_evidence = any(resource_types.get(t, 0) > 0 for t in related_types)
            well_arch_questions.append({
                "id": qid,
                "question": qdata.get("question", ""),
                "best_practices": qdata.get("best_practices", []),
                "evidence_present": has_evidence,
                "status": "compliant" if has_evidence else "review",
            })

        return {
            "evidence": evidence,
            "well_architected_questions": well_arch_questions,
            "summary": f"{len(evidence)} evidencias, {len(well_arch_questions)} preguntas Well-Architected.",
        }
