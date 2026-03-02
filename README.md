# OCI Well-Architected Diagnostic Toolkit

Herramienta de diagnóstico para evaluar cargas de trabajo en **Oracle Cloud Infrastructure (OCI)** según un marco tipo Well-Architected. Recolecta inventario vía **Resource Search**, recomendaciones de **Cloud Advisor (Optimizer)** y genera evidencias y reportes.

## Requisitos

- Python 3.8+
- Configuración OCI: archivo `~/.oci/config` (tras `oci setup config`) o variables de entorno / Instance Principal
- Permisos de lectura: Resource Search, Optimizer (Cloud Advisor), Identity (compartments)

## Instalación

```bash
cd diagnostic-toolkit-oci
pip install -r requirements.txt
```

## Configuración OCI

1. **Config file (recomendado para desarrollo):**

   ```bash
   oci setup config
   ```

   Se crea `~/.oci/config` con `user`, `fingerprint`, `tenancy`, `region` y la ruta a la clave privada.

2. **Variables de entorno** (útil para CI o sin archivo):

   - `OCI_CLI_USER` – OCID del usuario
   - `OCI_CLI_FINGERPRINT` – fingerprint de la API key
   - `OCI_CLI_TENANCY` – OCID del tenancy
   - `OCI_CLI_REGION` – región (ej. `us-phoenix-1`)
   - `OCI_CLI_KEY_FILE` – ruta a la clave privada (o contenido en variable si el SDK lo soporta)

3. **Instance Principal** (desde un compute OCI): no hace falta config file; el SDK usa la identidad del instance.

## Guía paso a paso

### 1. Instalar

```bash
pip install -r requirements.txt
```

### 2. Comportamiento por defecto (todo el tenancy)

Sin opciones, el tool usa el tenancy root y lista/compartments desde Identity; Resource Search y Optimizer operan sobre ese ámbito.

```bash
python3 ecad_oci.py full
```

### 3. Restringir a ciertos compartments

```bash
python3 ecad_oci.py full --compartments "ocid1.compartment.oc1..xxx,ocid1.compartment.oc1..yyy"
```

O con variable de entorno:

```bash
export OCI_COMPARTMENT_IDS="ocid1.compartment.oc1..xxx,ocid1.compartment.oc1..yyy"
python3 ecad_oci.py full
```

### 4. Comandos por pasos

```bash
python3 ecad_oci.py collect [--run-dir runs/mi-run] [--compartments id1,id2]
python3 ecad_oci.py analyze <run_dir>
python3 ecad_oci.py evidence <run_dir>
python3 ecad_oci.py reports <run_dir>
```

Si no se indica `--run-dir` en `collect` o `full`, se crea `runs/run-YYYYMMDD-HHMMSS`.

## Estructura de un run

- **raw/**  
  - `metadata.json` – tenancy y compartments  
  - `resource_search_resources.json` / `resource_search_counts.json` – inventario Resource Search  
  - `optimizer_recommendations.json` – recomendaciones Cloud Advisor  
- **index/index.json** – índice (tipos de recurso, recomendaciones por categoría)  
- **outputs/inventory.json** – inventario resumido  
- **outputs/findings.json** – hallazgos desde Cloud Advisor  
- **outputs/evidence/evidence_pack.json** – evidencias por pilar  
- **outputs/reports/** – reportes en Markdown (resumen ejecutivo, scorecard, hallazgos, plan de mejoras)

## Referencias

- [OCI Resource Search](https://docs.oracle.com/en-us/iaas/Content/Search/Concepts/resourcesearch.htm)
- [OCI Cloud Advisor (Optimizer)](https://docs.oracle.com/en-us/iaas/Content/cloud-advisor/home.htm)
- [OCI Python SDK](https://oracle-cloud-infrastructure-python-sdk.readthedocs.io/)
