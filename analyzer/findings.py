"""
Findings - Hallazgos a partir de recomendaciones de OCI Cloud Advisor (Optimizer).
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

CATEGORY_TO_PILLAR = {
    "cost_optimization": "Cost Optimization",
    "performance": "Performance Efficiency",
    "high_availability": "Reliability",
    "security": "Security",
    "operational_excellence": "Operational Excellence",
    "all": "Operational Excellence",
}


def get_findings_from_optimizer(index: Dict) -> List[Dict]:
    """Convertir recomendaciones del Optimizer en hallazgos para reportes."""
    findings = []
    recs_by_cat = index.get("recommendations_by_category", {})
    for category, recs in recs_by_cat.items():
        pillar = CATEGORY_TO_PILLAR.get(category, category)
        for rec in recs:
            importance = rec.get("importance", "MODERATE")
            impact = "High" if importance in ("CRITICAL", "HIGH") else "Medium" if importance == "MODERATE" else "Low"
            findings.append({
                "id": rec.get("id") or rec.get("name") or "",
                "domain": pillar,
                "category": category,
                "impact": impact,
                "description": rec.get("description") or "Recomendación OCI Cloud Advisor",
                "short_description": (rec.get("description") or "Recomendación OCI Cloud Advisor")[:200],
                "recommendation": "Revisar en OCI Console > Cloud Advisor",
                "source": "OCI Cloud Advisor",
            })
    return findings
