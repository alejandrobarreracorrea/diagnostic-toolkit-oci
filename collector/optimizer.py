"""
Optimizer (Cloud Advisor) - Recomendaciones OCI alineadas a Well-Architected.
"""

import logging
from typing import Dict, Any, List

logger = logging.getLogger(__name__)

# Categorías OCI Optimizer -> pilares
CATEGORY_TO_PILLAR = {
    "cost_optimization": "Cost Optimization",
    "performance": "Performance Efficiency",
    "high_availability": "Reliability",
    "security": "Security",
    "operational_excellence": "Operational Excellence",
}


class OptimizerCollector:
    """Recolecta recomendaciones de OCI Cloud Advisor (Optimizer)."""

    def __init__(self, config: Dict[str, Any], compartment_ids: List[str]):
        self.config = config
        self.compartment_ids = compartment_ids

    def collect_recommendations(self) -> Dict[str, Any]:
        """Listar recomendaciones para cada compartment (Cloud Advisor / Optimizer)."""
        try:
            import oci
            client = oci.optimizer.OptimizerClient(self.config)
            all_recommendations = []
            errors = []
            # Listar categorías disponibles y luego recomendaciones por categoría
            try:
                cat_response = client.list_categories(compartment_id=self.compartment_ids[0], limit=50)
                cat_data = getattr(cat_response, "data", None)
                cat_items = getattr(cat_data, "items", None) or []
                categories = [(getattr(c, "name", ""), getattr(c, "id", "")) for c in cat_items]
            except Exception as e:
                logger.warning("No se pudieron listar categorías Optimizer: %s", e)
                categories = []
            for comp_id in self.compartment_ids:
                if categories:
                    for cat_name, cat_id in categories:
                        try:
                            next_page = None
                            while True:
                                response = client.list_recommendations(
                                    compartment_id=comp_id,
                                    compartment_id_in_subtree=True,
                                    category_id=cat_id,
                                    limit=100,
                                    page=next_page,
                                )
                                rec_items = getattr(response.data, "items", None) or []
                                for rec in rec_items:
                                    all_recommendations.append(
                                        self._to_dict(rec, cat_name.lower().replace(" ", "_"), comp_id)
                                    )
                                next_page = getattr(response.data, "next_page", None) or getattr(response, "next_page", None)
                                if not next_page:
                                    break
                        except Exception as e:
                            logger.warning("Error listando recomendaciones %s: %s", cat_name, e)
                            errors.append({"compartment_id": comp_id, "category": cat_name, "error": str(e)})
                else:
                    try:
                        next_page = None
                        while True:
                            response = client.list_recommendations(
                                compartment_id=comp_id,
                                compartment_id_in_subtree=True,
                                limit=100,
                                page=next_page,
                            )
                            rec_items = getattr(response.data, "items", None) or []
                            for rec in rec_items:
                                all_recommendations.append(self._to_dict(rec, "all", comp_id))
                            next_page = getattr(response.data, "next_page", None) or getattr(response, "next_page", None)
                            if not next_page:
                                break
                    except TypeError:
                        errors.append({"compartment_id": comp_id, "error": "category_id required"})
                    except Exception as e:
                        logger.warning("Error listando recomendaciones: %s", e)
                        errors.append({"compartment_id": comp_id, "error": str(e)})
            return {
                "success": len(all_recommendations) > 0 or len(errors) == 0,
                "recommendations": all_recommendations,
                "total": len(all_recommendations),
                "errors": errors,
            }
        except Exception as e:
            logger.exception("Error Optimizer: %s", e)
            return {"success": False, "recommendations": [], "total": 0, "errors": [str(e)]}

    def _to_dict(self, rec, category: str, compartment_id: str) -> Dict:
        return {
            "compartment_id": compartment_id,
            "id": getattr(rec, "id", None),
            "name": getattr(rec, "name", None),
            "category": category,
            "importance": getattr(rec, "importance", None) or "MEDIUM",
            "resource_counts": getattr(rec, "resource_counts", None),
            "description": getattr(rec, "description", None) or "",
            "lifecycle_state": getattr(rec, "lifecycle_state", None),
        }
