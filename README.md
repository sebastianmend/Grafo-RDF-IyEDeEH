# Grafo de Conocimiento sobre Agricultura de Precisión

**Proyecto de Interoperabilidad y Explotación de Datos en Ecosistemas Heterogéneos (BIM1) - UTPL**

Construcción de un grafo de conocimiento a partir de publicaciones científicas sobre Agricultura de Precisión, desde la extracción de datos hasta su almacenamiento en GraphDB.

---

## 👥 Integrantes

- **Jean Villavicencio**
- **Samuel Reyes**
- **Sebastian Mendieta**

---

## 📋 Descripción del Proyecto

Este proyecto implementa un pipeline completo de ETL (Extract, Transform, Load) para construir un grafo de conocimiento sobre **Agricultura de Precisión** a partir de la API de Semantic Scholar. El proyecto se divide en tres fases:

1. **Fase 1**: Extracción, enriquecimiento y estructuración de datos académicos
2. **Fase 2**: Conversión de datos a formato RDF y almacenamiento en GraphDB
3. **Fase 3**: Análisis y explotación del grafo (futuro)

### Dominio: Agricultura de Precisión

La Agricultura de Precisión integra datos geoespaciales y temporales (mapas de rendimiento, humedad, índices de vegetación, sensores en campo, imágenes de drones/satélites) y modelos de ML/IA para decidir con precisión dónde, cuánto y cuándo intervenir. El objetivo es producir más y mejor con menos insumos, reduciendo impacto ambiental y costos.

Este dominio es ideal para un grafo de conocimiento porque los papers conectan tecnologías (sensores, UAV, IoT), prácticas (riego/fertilización variable), cultivos, regiones y resultados medibles (rendimiento, eficiencia hídrica, huella ambiental), generando relaciones ricas y consultables.

---

## 🎯 Objetivos del Proyecto

### Fase 1: Extracción de Datos
- Extraer 1,000 publicaciones semilla sobre "precision agriculture" desde Semantic Scholar
- Enriquecer cada paper con metadatos completos (venue, citas, autores, referencias, campos de estudio)
- Construir un grafo de citaciones (relación CITES) sin self-edges ni duplicados
- Generar CSVs estructurados con nodos y relaciones
- Enriquecer top 200 autores con afiliaciones institucionales

### Fase 2: Conversión RDF y GraphDB
- Convertir los datos extraídos y preprocesados a formato RDF según modelo común
- Utilizar vocabularios estándar (Schema.org, DCT, SKOS)
- Almacenar los datos en GraphDB
- Validar el modelo mediante consultas SPARQL

---

## 📦 Entregables

### Fase 1
- ✅ Notebook Jupyter con código de extracción y transformación
- ✅ 10 archivos CSV en `data/processed/` (nodos y relaciones)
- ✅ Esquema del modelo de datos (`data_model/schema.yml`)
- ✅ Notebook HTML exportado con resultados y visualizaciones

### Fase 2
- ✅ Datos RDF en formato Turtle (`notebooks/out/agri_graph.ttl`) y N-Triples (`agri_graph.nt`)
- ✅ Notebook HTML utilizado para convertir los datos a RDF
- ⚠️ Datos RDF subidos en GraphDB (pendiente de ejecución)
- ⚠️ Informe PDF que resuma las tres fases del proyecto con imágenes de GraphDB

---

## 🗂️ Estructura del Proyecto

```
.
├── data_model/
│   └── schema.yml                    # Esquema del grafo (nodos y relaciones)
├── notebooks/
│   ├── 01_extraccion_precision_agri.ipynb    # Notebook principal
│   ├── 01_extraccion_precision_agri.html     # Notebook exportado a HTML
│   ├── data/
│   │   ├── processed/                # CSVs finales (nodos y relaciones)
│   │   │   ├── papers.csv
│   │   │   ├── authors.csv
│   │   │   ├── venues.csv
│   │   │   ├── fields.csv
│   │   │   ├── paper_authoredby_author.csv
│   │   │   ├── paper_publishedin_venue.csv
│   │   │   ├── paper_has_topic.csv
│   │   │   ├── paper_cites_paper.csv
│   │   │   ├── author_affiliations.csv
│   │   │   └── authors_enriched.csv
│   │   └── raw/                      # Datos crudos (JSONs de la API)
│   └── out/                          # Archivos RDF generados
│       ├── agri_graph.ttl            # RDF en formato Turtle
│       └── agri_graph.nt             # RDF en formato N-Triples
├── src/
│   ├── config.py                     # Configuración (API key, URLs)
│   ├── semanticscholar_client.py    # Cliente HTTP para Semantic Scholar API
│   └── etl.py                        # Funciones de ETL (extracción, transformación)
├── .env                              # API key (NO commitear)
├── requirements.txt                  # Dependencias Python
├── README.md                         # Este archivo
├── VERIFICACION_REQUISITOS.md        # Checklist Fase 1
└── VERIFICACION_FASE2.md             # Checklist Fase 2
```

---

## 🚀 Instalación y Configuración

### Prerrequisitos

- Python 3.10 o superior
- API Key de Semantic Scholar (gratis en https://www.semanticscholar.org/product/api)

### Instalación

```bash
# Clonar el repositorio
git clone <URL_DEL_REPO>
cd Bim1InteroperabilidadDatos-main

# Crear entorno virtual
python -m venv .venv

# Activar el entorno
# En Windows:
.venv\Scripts\activate
# En Linux/Mac:
source .venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar dependencias adicionales para RDF (si no están en requirements.txt)
pip install rdflib
```

### Configuración de API Key

Crea un archivo `.env` en la raíz del proyecto:

```env
S2_API_KEY=tu_api_key_aqui
```

**⚠️ Importante**: No incluyas el archivo `.env` en el repositorio (está en `.gitignore`).

---

## 📖 Uso del Proyecto

### Fase 1: Extracción de Datos

1. **Abrir el notebook**:
   ```bash
   jupyter notebook notebooks/01_extraccion_precision_agri.ipynb
   ```
   O desde VS Code: abre el archivo `.ipynb` directamente.

2. **Ejecutar el notebook completo**:
   - El notebook ejecuta automáticamente:
     - Búsqueda de 1,000 papers con filtros específicos
     - Descarga de detalles enriquecidos
     - Construcción del grafo CITES
     - Enriquecimiento de afiliaciones de autores
     - Generación de resúmenes y métricas
     - Exportación de CSVs

3. **Tiempo estimado**: 20-30 minutos (depende de rate limits de la API)

4. **Exportar a HTML**:
   - Ejecuta la **celda 11** del notebook para exportación automática
   - O manualmente: `jupyter nbconvert --to html notebooks/01_extraccion_precision_agri.ipynb`

### Fase 2: Conversión RDF y GraphDB

1. **Generar RDF**:
   - Ejecuta la **celda 12** del notebook
   - Esto genera `notebooks/out/agri_graph.ttl` y `agri_graph.nt`

2. **Cargar en GraphDB**:
   - Sigue las instrucciones detalladas en la **celda 13** del notebook:
     1. Crear repositorio `agri-precision` en GraphDB
     2. Configurar prefijos (ex, schema, dct, skos)
     3. Importar `agri_graph.ttl`
     4. Ejecutar consultas SPARQL de validación
     5. Tomar capturas de pantalla para el informe

---

## 🔍 Filtros y Parámetros API Utilizados

### Endpoint: `/paper/search/bulk`

```python
{
    "query": "precision agriculture",
    "year": "2018-",
    "publicationTypes": "JournalArticle,Conference,Review,Proceedings,Survey",
    "sort": "publicationDate",
    "fields": "title,year,url,publicationTypes,publicationDate,citationCount",
    "token": "<pagination_token>"  # Para paginación
}
```

### Endpoint: `/paper/{paperId}`

```python
{
    "fields": "paperId,title,year,abstract,citationCount,influentialCitationCount,"
              "authors,externalIds,url,publicationTypes,venue,fieldsOfStudy,"
              "references.paperId"
}
```

### Endpoint: `/author/{authorId}`

```python
{
    "fields": "authorId,name,affiliations,url,paperCount,citationCount"
}
```

**Limitaciones respetadas:**
- Rate limit: 100 req/5min (free tier) → se usa backoff exponencial
- Máx 1,000 papers por request en bulk search
- Campos anidados (`authors.affiliations`) no disponibles en Graph v1 → enriquecimiento posterior

---

## 🧩 Modelo de Datos

El modelo de grafo se define en `data_model/schema.yml`:

### Nodos

- **Paper**: publicación científica (paperId, title, year, abstract, citationCount, doi, url, publicationTypes, venue)
- **Author**: autor (authorId, name, url)
- **Venue**: revista o conferencia (venueId, name)
- **Field**: campo de estudio (fieldName)

### Relaciones

- **AUTHORED_BY**: Paper → Author (mapeado a `schema:author` en RDF)
- **PUBLISHED_IN**: Paper → Venue (mapeado a `schema:isPartOf` en RDF)
- **HAS_TOPIC**: Paper → Field (mapeado a `dct:subject` en RDF)
- **CITES**: Paper → Paper (mapeado a `schema:citation` en RDF)

### Vocabularios RDF Utilizados

- **Schema.org**: Article, Person, Periodical, Organization, author, isPartOf, citation
- **Dublin Core Terms (DCT)**: subject
- **SKOS**: Concept, prefLabel

---

## 📊 Archivos Generados

### CSVs en `data/processed/`

| Archivo | Descripción | Registros Aprox. |
|---------|-------------|------------------|
| `papers.csv` | Nodos de papers (1,000 semilla + stubs) | ~6,772 |
| `authors.csv` | Nodos de autores únicos | ~3,405 |
| `venues.csv` | Nodos de venues (revistas, conferencias) | ~446 |
| `fields.csv` | Nodos de campos de estudio | ~17 |
| `paper_authoredby_author.csv` | Relación Paper → Author | ~3,826 |
| `paper_publishedin_venue.csv` | Relación Paper → Venue | ~786 |
| `paper_has_topic.csv` | Relación Paper → Field | ~1,349 |
| `paper_cites_paper.csv` | Relación CITES (Paper → Paper) | ~6,328 |
| `author_affiliations.csv` | Afiliaciones de top 200 autores | Variable |
| `authors_enriched.csv` | Autores con paperCount y citationCount | 200 |

### Archivos RDF en `notebooks/out/`

- `agri_graph.ttl`: RDF en formato Turtle (~10-11 MB)
- `agri_graph.nt`: RDF en formato N-Triples (~10-11 MB)

---

## 📈 Métricas y Resúmenes

El notebook genera automáticamente:

1. **Distribución temporal**: gráfica de publicaciones por año
2. **Top 10 venues**: revistas/conferencias con más papers
3. **Top 10 autores**: autores más prolíficos
4. **Top 15 papers influyentes**: por `influentialCitationCount`
5. **Métricas del grafo CITES**:
   - Total de aristas: ~6,328
   - Papers que citan (sources): ~327 (2.4%)
   - Papers citados (targets): ~12,815 (93.2%)
   - Self-edges: 0
   - Duplicados: 0

---

## 🔧 Consultas SPARQL para GraphDB

Una vez importado el RDF en GraphDB, puedes ejecutar estas consultas:

### A. Artículos con autores, venue y conceptos

```sparql
PREFIX schema: <http://schema.org/>
PREFIX dct:    <http://purl.org/dc/terms/>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>

SELECT ?art ?title ?author ?venue ?concept
WHERE {
  ?a a schema:Article ; schema:title ?title .
  OPTIONAL { ?a schema:author / schema:name ?author }
  OPTIONAL { ?a schema:isPartOf / schema:name ?venue }
  OPTIONAL { ?a dct:subject / skos:prefLabel ?concept }
  BIND(STR(?a) AS ?art)
}
LIMIT 25
```

### B. Top conceptos por cantidad de artículos

```sparql
PREFIX schema: <http://schema.org/>
PREFIX dct:    <http://purl.org/dc/terms/>
PREFIX skos:   <http://www.w3.org/2004/02/skos/core#>

SELECT ?concept ?label (COUNT(?a) AS ?n)
WHERE {
  ?a a schema:Article ; dct:subject ?c .
  ?c skos:prefLabel ?label .
  BIND(STR(?c) AS ?concept)
}
GROUP BY ?concept ?label
ORDER BY DESC(?n)
LIMIT 10
```

### C. Citas (paper → paper)

```sparql
PREFIX schema: <http://schema.org/>

SELECT ?fromTitle ?toTitle
WHERE {
  ?from a schema:Article ; schema:citation ?to ;
        schema:title ?fromTitle .
  OPTIONAL { ?to schema:title ?toTitle }
}
LIMIT 25
```

---

## 📝 Texto para el Informe PDF

### Fase 1: Extracción y Enriquecimiento

> **Cobertura y enriquecimiento.** Se recolectaron *1,000* publicaciones semilla desde *Semantic Scholar* (Graph API /paper/search/bulk) con la consulta "precision agriculture", filtros year=2018-, publicationTypes=JournalArticle,Conference,Review,Proceedings,Survey, y orden publicationDate. Para cada publicación se consultó /paper/{id} con fields específicos: venue (string), publicationTypes, citationCount, influentialCitationCount, externalIds.DOI, url, authors y references.paperId.

> **Grafo de citación.** A partir de references.paperId se generó la relación *CITES* (paper → paper citado), eliminando auto-citas y duplicados. Se incorporaron *nodos stub* para referencias externas no presentes en el conjunto base, con lo cual se preservan todas las conexiones.

> **Modelo de datos y reuso de vocabulario.** Nodos: Paper, Author, Venue, Field; relaciones: *AUTHORED_BY* (≈schema:author), *PUBLISHED_IN* (≈schema:isPartOf), *HAS_TOPIC* (≈schema:about), *CITES* (≈schema:citation).

> **Exploración y métricas.** Se incluyen la distribución temporal, top venues, top autores y un ranking por influentialCitationCount; además, métricas de conectividad del grafo (porcentaje de papers que citan y que son citados).

> **Autores y afiliaciones.** Se enriquecieron los top 200 autores más prolíficos con llamadas al endpoint /author/{id}, obteniendo sus afiliaciones institucionales (cuando están disponibles), número total de publicaciones y conteo de citas.

> **Apuntes de implementación.** Se manejaron límites de tasa con backoff y *reintentos selectivos* (de 998→*1000/1000*). El campo venue se maneja como string por restricciones de campos en Graph v1; se reporta el url del paper como enlace principal.

### Fase 2: Conversión RDF y GraphDB

> **Modelo RDF y vocabularios estándar.** Los datos extraídos y preprocesados (CSVs en `data/processed/`) se convirtieron a formato RDF usando vocabularios estándar: Schema.org para entidades principales (Article, Person, Periodical, Organization), Dublin Core Terms (DCT) para subjects, y SKOS para conceptos. El modelo RDF preserva la estructura del grafo definida en `data_model/schema.yml`, mapeando Papers a `schema:Article`, Authors a `schema:Person`, Venues a `schema:Periodical`, y Fields a `skos:Concept`. Las relaciones se representan mediante propiedades estándar: `schema:author` (AUTHORED_BY), `schema:isPartOf` (PUBLISHED_IN), `dct:subject` (HAS_TOPIC), y `schema:citation` (CITES).

> **Generación de triples.** Se generaron dos formatos de salida: Turtle (TTL) y N-Triples (NT), con un total de aproximadamente [N] triples RDF. El archivo principal `agri_graph.ttl` tiene un tamaño de ~10-11 MB y contiene todas las entidades y relaciones del grafo de conocimiento.

> **Almacenamiento en GraphDB.** Se creó el repositorio `agri-precision` en GraphDB con configuración estándar (RDF4J, OWL-Horst). Se configuraron los namespaces necesarios: `ex` (http://example.org/agri#), `schema` (http://schema.org/), `dct` (http://purl.org/dc/terms/), y `skos` (http://www.w3.org/2004/02/skos/core#). El archivo RDF se importó exitosamente, preservando la integridad de todos los triples.

> **Exploración y consultas SPARQL.** Se realizaron consultas SPARQL para validar el modelo y explorar el grafo: (1) artículos con sus autores, venues y conceptos asociados; (2) top conceptos por cantidad de artículos; (3) relaciones de citación entre papers. El visualizador de grafo de GraphDB permite explorar las conexiones entre Article, Person, Periodical y Concept, confirmando la estructura del modelo de conocimiento.

---

## 🛠️ Solución de Problemas

### Error: "API Key cargada: ❌ No"

1. Verifica que `.env` existe en la raíz del proyecto
2. El contenido debe ser: `S2_API_KEY=tu_key_aqui` (sin espacios extras)
3. Reinicia el kernel del notebook

### Error: "Rate limit exceeded (429)"

- El código ya maneja esto con backoff automático
- Si persiste, aumenta el delay en `time.sleep()` en las celdas de retry

### Error: "Solo hay X candidatos; aumenta el target"

- Relaja los filtros en la celda 2:
  - Cambia `YEAR = "2018-"` a `"2010-"` o anterior
  - Añade más tipos en `PUB_TYPES`

### No se obtienen afiliaciones

- Semantic Scholar no siempre expone afiliaciones en Graph API v1
- Es normal que algunos autores no tengan este campo
- El código genera `author_affiliations.csv` solo con los disponibles

### Error al generar RDF

- Verifica que todos los CSVs existen en `data/processed/`
- Ejecuta primero todas las celdas de la Fase 1
- Revisa que `rdflib` esté instalado: `pip install rdflib`

---

## 📸 Capturas Necesarias para el Informe

Para el informe PDF final, necesitas tomar estas capturas de GraphDB:

1. **Repositorio creado** (`agri-precision`) en GraphDB
2. **Import success** (pantalla que muestra el conteo de triples después de importar)
3. **Visual Graph** con nodos Article–Person–Periodical–Concept (1-2 capturas)
4. **Resultados de consulta SPARQL A** (artículos con autores, venues, conceptos)
5. **Resultados de consulta SPARQL B** (top conceptos por cantidad)
6. **Resultados de consulta SPARQL C** (citas paper → paper)

---

## ✅ Checklist de Entregables

### Fase 1
- [x] Notebook con código de extracción (`01_extraccion_precision_agri.ipynb`)
- [x] 10 CSVs en `data/processed/`
- [x] Esquema del modelo (`data_model/schema.yml`)
- [x] Notebook HTML exportado (`01_extraccion_precision_agri.html`)

### Fase 2
- [x] Código de conversión RDF (celda 12 del notebook)
- [x] Archivos RDF generados (`agri_graph.ttl` y `agri_graph.nt`)
- [x] Instrucciones GraphDB (celda 13 del notebook)
- [ ] RDF importado en GraphDB (pendiente de ejecución)
- [ ] Capturas de GraphDB tomadas (pendiente)
- [ ] Informe PDF final creado (pendiente)

---

## 🔗 Referencias

- **Semantic Scholar API Docs**: https://api.semanticscholar.org/api-docs/graph
- **Schema.org Vocabulary**: https://schema.org/
- **Dublin Core Terms**: http://purl.org/dc/terms/
- **SKOS**: https://www.w3.org/2004/02/skos/core
- **GraphDB Documentation**: https://graphdb.ontotext.com/documentation/

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la UTPL - Interoperabilidad y Explotación de Datos en Ecosistemas Heterogéneos (BIM1).

---

## 📚 Documentación Adicional

- `VERIFICACION_REQUISITOS.md`: Checklist completo de la Fase 1
- `VERIFICACION_FASE2.md`: Checklist completo de la Fase 2
- `data_model/schema.yml`: Esquema del modelo de datos

---

**Última actualización**: Diciembre 2024
