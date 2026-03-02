"""
Resource Search - Inventario de recursos OCI en el tenancy.
"""

import logging
from typing import Dict, Any, List
from collections import Counter

logger = logging.getLogger(__name__)


class ResourceSearchCollector:
    """Recolecta inventario de recursos vía OCI Resource Search."""

    def __init__(self, config: Dict[str, Any], compartment_ids: List[str] = None):
        self.config = config
        self.compartment_ids = compartment_ids or [config.get("tenancy")]

    def search_resources(self) -> Dict[str, Any]:
        """Buscar todos los recursos en el tenancy (Resource Search)."""
        try:
            import oci
            from oci.resource_search.models import StructuredSearchDetails
            client = oci.resource_search.ResourceSearchClient(self.config)
            search_details = StructuredSearchDetails(query="query all resources", type="Structured")
            all_items = []
            next_page = None
            while True:
                response = client.search_resources(
                    search_details=search_details,
                    limit=1000,
                    page=next_page,
                )
                items = getattr(response.data, "items", None) or []
                for item in items:
                    all_items.append({
                        "identifier": item.identifier,
                        "compartment_id": getattr(item, "compartment_id", None),
                        "resource_type": getattr(item, "resource_type", None) or "",
                        "display_name": getattr(item, "display_name", None) or "",
                        "lifecycle_state": getattr(item, "lifecycle_state", None),
                    })
                next_page = getattr(response.data, "next_page", None) or getattr(response, "next_page", None)
                if not next_page:
                    break
            return {
                "success": True,
                "data": all_items,
                "total_records": len(all_items),
            }
        except Exception as e:
            logger.exception("Error en Resource Search: %s", e)
            return {"success": False, "error": str(e), "data": []}

    def collect_counts(self) -> Dict[str, Any]:
        """Conteos por tipo de recurso."""
        result = self.search_resources()
        if not result.get("success") or not result.get("data"):
            return result
        types = [r.get("resource_type") or "Unknown" for r in result["data"]]
        counts = [{"resource_type": k, "count": v} for k, v in Counter(types).most_common()]
        return {
            "success": True,
            "data": counts,
            "total_records": len(result["data"]),
        }
