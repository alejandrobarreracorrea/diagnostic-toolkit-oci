# Well-Architected Scorecard - OCI

**Fecha:** {{ date }}

**Framework:** OCI Well-Architected (versión {{ well_arch_version }})

---

## Resumen de puntuaciones

Evaluación por los 6 pilares. Escala 1 (crítico) a 5 (excelente).

**Puntuación media:** {{ "%.1f" | format(average_score) }}/5.0

---

## Puntuación por pilar

{% for domain, score in domain_scores.items() %}

### {{ domain }}

**Puntuación: {{ score }}/5**

{% if score == 5 %}
✅ **Excelente** - Sin problemas significativos en este pilar.
{% elif score == 4 %}
✅ **Bueno** - Arquitectura sólida con mejoras menores.
{% elif score == 3 %}
⚠️ **Aceptable** - Áreas de mejora identificadas.
{% elif score == 2 %}
⚠️ **Necesita mejora** - Requiere atención.
{% else %}
❌ **Crítico** - Acción inmediata recomendada.
{% endif %}

{% endfor %}

---

**Referencia:** [OCI Cloud Advisor](https://docs.oracle.com/en-us/iaas/Content/cloud-advisor/home.htm).
