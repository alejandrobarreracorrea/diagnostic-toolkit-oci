# Executive Summary - OCI Well-Architected Diagnostic

**Fecha:** {{ date }}  
**Tenancy:** {{ tenancy_id }}  
**Compartments:** {{ compartments_count }}  
**Framework:** OCI Well-Architected (versión {{ well_arch_version }})

---

## Resumen Ejecutivo

Este reporte presenta los hallazgos del diagnóstico arquitectónico realizado en el tenancy OCI. El análisis se realizó mediante Resource Search y Cloud Advisor (Optimizer).

### Métricas Principales

- **Compartments evaluados:** {{ compartments_count }}
- **Total de recursos:** {{ total_resources }}
- **Tipos de recurso distintos:** {{ resource_types_count }}
- **Hallazgos (Cloud Advisor):** {{ findings_count }}

### Top tipos de recurso

{% for r in top_resource_types %}
- **{{ r.type }}**: {{ r.count }} recursos
{% endfor %}

---

## Conclusiones

Este diagnóstico proporciona:

1. **Inventario**: Recursos y tipos desde Resource Search
2. **Evidencias Well-Architected**: Datos para los 6 pilares
3. **Recomendaciones**: OCI Cloud Advisor (Cost, Performance, High Availability, Security, Operational Excellence)
4. **Plan de mejoras**: Priorización según impacto

### Próximos pasos

1. Revisar reporte de hallazgos y scorecard
2. Ejecutar revisión Well-Architected usando el evidence pack
3. Priorizar acciones según el plan de mejoras
4. Implementar recomendaciones de Cloud Advisor

---

**Referencia:** [OCI Cloud Advisor](https://docs.oracle.com/en-us/iaas/Content/cloud-advisor/home.htm).
