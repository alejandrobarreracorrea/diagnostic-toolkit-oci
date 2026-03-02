"""
Metadata Collector - Tenancy y compartments OCI.
"""

import logging
from datetime import datetime
from typing import Dict, Any, List

logger = logging.getLogger(__name__)


class MetadataCollector:
    """Recolector de metadatos del tenancy y compartments OCI."""

    def __init__(self, config: Dict[str, Any], compartment_ids: List[str] = None):
        self.config = config
        self.compartment_ids = compartment_ids

    def collect(self) -> Dict[str, Any]:
        """Recolectar tenancy y lista de compartments."""
        metadata = {
            "tenancy_id": self.config.get("tenancy"),
            "compartment_ids": [],
            "compartments": [],
            "timestamp": datetime.utcnow().isoformat(),
        }
        try:
            import oci
            identity = oci.identity.IdentityClient(self.config)
            tenancy_id = self.config["tenancy"]
            metadata["compartments"].append({
                "id": tenancy_id,
                "name": "root",
                "description": "Tenancy root compartment",
            })
            metadata["compartment_ids"].append(tenancy_id)
            try:
                list_response = identity.list_compartments(
                    compartment_id=tenancy_id,
                    compartment_id_in_subtree=True,
                    access_level="ANY",
                    lifecyclestate="ACTIVE",
                )
                for c in list_response.data:
                    metadata["compartments"].append({
                        "id": c.id,
                        "name": c.name,
                        "description": getattr(c, "description", None) or "",
                    })
                    metadata["compartment_ids"].append(c.id)
            except Exception as e:
                logger.warning("Error listando compartments: %s", e)
            if self.compartment_ids:
                metadata["scope_compartment_ids"] = self.compartment_ids
        except Exception as e:
            logger.warning("Error recolectando metadata OCI: %s", e)
        return metadata
