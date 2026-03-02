# Plan de mejoras - OCI Well-Architected

**Fecha:** {{ date }}

**Framework:** OCI Well-Architected (versión {{ well_arch_version }})

- **Pronta solución (30 días):** hallazgos de alto/medio impacto.
- **Mayor complejidad (MRI):** resto de hallazgos y preguntas Well-Architected sin evidencia suficiente.

Fuentes: OCI Cloud Advisor y evidence pack.

---

## 1. Pronta solución (30 días)

{% for finding in improvement_plan_pronta %}
### {{ finding.short_description or finding.description or finding.id }}

- **Dominio:** {{ finding.domain }}
- **Impacto:** {{ finding.impact }}
- **Descripción:** {{ finding.description }}
- **Recomendación:** {{ finding.recommendation }}
- **Origen:** {{ finding.source }}

{% endfor %}
{% if not improvement_plan_pronta %}
*No se identificaron tareas de pronta solución en este diagnóstico.*
{% endif %}

---

## 2. Mejoras de mayor complejidad (MRI)

{% for finding in improvement_plan_mri %}
### {{ finding.title or finding.short_description or finding.description or finding.id }}

- **Dominio:** {{ finding.domain }}
- **Impacto:** {{ finding.impact }}
- **Descripción:** {{ finding.description }}
- **Recomendación:** {{ finding.recommendation }}
{% if finding.source %}- **Origen:** {{ finding.source }}{% endif %}

{% endfor %}
{% if not improvement_plan_mri %}
*No hay MRI en este diagnóstico.*
{% endif %}

---

**Referencia:** [OCI Cloud Advisor](https://docs.oracle.com/en-us/iaas/Content/cloud-advisor/home.htm).
