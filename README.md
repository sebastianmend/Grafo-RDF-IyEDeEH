# Precision Agriculture Knowledge Graph - Fase 1: Extracción de Datos

Proyecto de **Interoperabilidad de Datos** (BIM1) - UTPL  
**Extracción y modelado de publicaciones académicas sobre agricultura de precisión desde Semantic Scholar**

---

## 📋 Descripción

Este proyecto implementa la **Fase 1** del trabajo: extracción, enriquecimiento y estructuración de datos académicos para construir un grafo de conocimiento sobre *precision agriculture*. 

Se utiliza la **Semantic Scholar Graph API** para:
- Buscar y filtrar publicaciones científicas
- Enriquecer cada paper con metadatos detallados
- Construir un grafo de citaciones (relación CITES)
- Extraer autores, venues, campos de estudio y sus relaciones

---

## 🎯 Objetivos Cumplidos

### ✅ Requisitos Esenciales (según audio de la profesora)

- [x] **1,000 papers semilla** (dentro del rango 500-1,000; máx 5,000)
- [x] **Enriquecimiento por ID** de cada paper:
  - `venue` (string)
  - `publicationTypes`
  - `citationCount`
  - `influentialCitationCount`
  - `externalIds.DOI`
  - `url`
  - `authors`
  - `references.paperId`
- [x] **Grafo de citación (CITES)**: construido desde `references.paperId`
  - Sin self-edges
  - Sin duplicados
  - Con *stubs* para citados externos (preserva todas las conexiones)
- [x] **Filtros API probados**:
  - `query`: "precision agriculture"
  - `year`: 2010-
  - `publicationTypes`: JournalArticle, Conference, Review, Proceedings, Survey
  - `sort`: publicationDate
  - Paginación con `token`
- [x] **Resúmenes generados**:
  - Distribución temporal (por año)
  - Top venues
  - Top autores
  - Top papers por influentialCitationCount
- [x] **Organización del código**:
  - Notebook con celdas de diagnóstico
  - Manejo de backoff y reintentos (998 → 1000/1000)
  - Esquema de datos declarado (YAML)
  - CSVs exportados en `data/processed/`
- [x] **Afiliaciones de autores**: enriquecimiento de top 200 autores con organizaciones

---

## 🗂️ Estructura del Proyecto

```
.
├── data/
│   ├── raw/              # Datos crudos (búsquedas, detalles JSON)
│   └── processed/        # CSVs finales (nodos y relaciones)
├── notebooks/
│   └── 01_extraccion_precision_agri.ipynb  # Notebook principal
├── src/
│   ├── config.py                            # Configuración (API key, URLs)
│   ├── semanticscholar_client.py           # Cliente HTTP para S2 API
│   └── etl.py                              # Funciones de ETL
├── schema/
│   └── kg_model.yaml                        # Modelo de datos (nodos, relaciones)
├── .env                                     # API key (NO commitear)
├── requirements.txt                         # Dependencias Python
└── README.md                                # Este archivo
```

---

## 🚀 Cómo Ejecutar

### 1. **Prerrequisitos**

- Python 3.10+
- API Key de Semantic Scholar (gratis en https://www.semanticscholar.org/product/api)

### 2. **Instalación**

```bash
# Clonar el repositorio (si aplica)
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
```

### 3. **Configurar API Key**

Crea un archivo `.env` en la raíz del proyecto:

```env
S2_API_KEY=tu_api_key_aqui
```

### 4. **Ejecutar el Notebook**

```bash
# Opción 1: Jupyter Notebook
jupyter notebook notebooks/01_extraccion_precision_agri.ipynb

# Opción 2: Jupyter Lab
jupyter lab notebooks/01_extraccion_precision_agri.ipynb

# Opción 3: VS Code
# Abre el .ipynb directamente en VS Code
```

**Nota:** El notebook ejecuta automáticamente:
1. Búsqueda de 1,000 papers
2. Descarga de detalles enriquecidos
3. Enriquecimiento de afiliaciones de autores
4. Construcción del grafo CITES
5. Generación de resúmenes y métricas
6. Exportación de CSVs

**Tiempo estimado:** 20-30 minutos (depende de rate limits de la API)

---

## 📊 Archivos Generados

Todos los CSVs se guardan en `data/processed/`:

| Archivo | Descripción | Registros Aprox. |
|---------|-------------|------------------|
| `papers.csv` | Nodos de papers (1,000 semilla + 5,772 stubs) | 6,772 |
| `authors.csv` | Nodos de autores únicos | 3,405 |
| `venues.csv` | Nodos de venues (revistas, conferencias) | 446 |
| `fields.csv` | Nodos de campos de estudio | 17 |
| `paper_authoredby_author.csv` | Relación Paper → Author | 3,826 |
| `paper_publishedin_venue.csv` | Relación Paper → Venue | 786 |
| `paper_has_topic.csv` | Relación Paper → Field | 1,349 |
| `paper_cites_paper.csv` | Relación CITES (Paper → Paper) | 6,328 |
| `author_affiliations.csv` | Afiliaciones de top 200 autores | Variable |
| `authors_enriched.csv` | Autores con paperCount y citationCount | 200 |

---

## 🔍 Filtros y Parámetros API Utilizados

### Endpoint: `/paper/search/bulk`

```python
{
    "query": "precision agriculture",
    "year": "2010-",
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

El modelo de grafo se define en `schema/kg_model.yaml`:

### Nodos

- **Paper**: publicación científica (paperId, title, year, abstract, citationCount, etc.)
- **Author**: autor (authorId, name, url)
- **Venue**: revista o conferencia (venueId, name)
- **Field**: campo de estudio (fieldId, name)

### Relaciones

- **AUTHORED_BY**: Paper → Author (≈ `schema:author`)
- **PUBLISHED_IN**: Paper → Venue (≈ `schema:isPartOf`)
- **HAS_TOPIC**: Paper → Field (≈ `schema:about`)
- **CITES**: Paper → Paper (≈ `schema:citation`)

**Vocabularios reusados:**
- Schema.org (author, isPartOf, about, citation)
- DBLP (para venues de CS)
- FOAF (para autores y afiliaciones)

---

## 📈 Métricas y Resúmenes

El notebook genera automáticamente:

1. **Distribución temporal**: gráfica de publicaciones por año
2. **Top 10 venues**: revistas/conferencias con más papers
3. **Top 10 autores**: autores más prolíficos
4. **Top 15 papers influyentes**: por `influentialCitationCount`
5. **Métricas del grafo CITES**:
   - Total de aristas: 6,328
   - Papers que citan (sources): 168 (2.5%)
   - Papers citados (targets): 5,811 (85.8%)
   - Self-edges: 0
   - Duplicados: 0

---

## 📦 Exportar a HTML

Para generar el notebook en formato HTML (requerido para el entregable):

### Opción 1: Desde el notebook (RECOMENDADO - AUTOMÁTICO) ⭐

**Ejecuta la última celda del notebook** (celda 13) que exporta automáticamente a HTML:
1. Abre el notebook `01_extraccion_precision_agri.ipynb`
2. Ve a la última celda (después de "🚀 Exportación Automática a HTML")
3. Ejecuta la celda
4. El archivo HTML se generará automáticamente en `notebooks/01_extraccion_precision_agri.html`

### Opción 2: Línea de comandos

```bash
jupyter nbconvert --to html notebooks/01_extraccion_precision_agri.ipynb
```

### Opción 3: VS Code

1. Abre el notebook en VS Code
2. Click en los tres puntos `...` en la barra superior
3. Selecciona **"Export"** → **"HTML"**
4. Guarda como `01_extraccion_precision_agri.html`

El HTML incluirá:
- Todo el código ejecutado
- Outputs, tablas y gráficas
- Secciones de verificación y diagnóstico

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
  - Cambia `YEAR = "2010-"` a `"2000-"`
  - Añade más tipos en `PUB_TYPES`

### No se obtienen afiliaciones

- Semantic Scholar no siempre expone afiliaciones en Graph API v1
- Es normal que algunos autores no tengan este campo
- El código genera `author_affiliations.csv` solo con los disponibles

---

## 📝 Texto para el Informe PDF (Fase 1)

> **Cobertura y enriquecimiento.** Se recolectaron *1,000* publicaciones semilla desde *Semantic Scholar* (Graph API /paper/search/bulk) con la consulta "precision agriculture", filtros year=2010-, publicationTypes=JournalArticle,Conference,Review,Proceedings,Survey, y orden publicationDate. Para cada publicación se consultó /paper/{id} con fields específicos: venue (string), publicationTypes, citationCount, influentialCitationCount, externalIds.DOI, url, authors y references.paperId.

> **Grafo de citación.** A partir de references.paperId se generó la relación *CITES* (paper → paper citado), eliminando auto-citas y duplicados. Se incorporaron *nodos stub* para referencias externas no presentes en el conjunto base, con lo cual se preservan todas las conexiones.

> **Modelo de datos y reuso de vocabulario.** Nodos: Paper, Author, Venue, Field; relaciones: *AUTHORED_BY* (≈schema:author), *PUBLISHED_IN* (≈schema:isPartOf), *HAS_TOPIC* (≈schema:about), *CITES* (≈schema:citation).

> **Exploración y métricas.** Se incluyen la distribución temporal, top venues, top autores y un ranking por influentialCitationCount; además, métricas de conectividad del grafo (porcentaje de papers que citan y que son citados).

> **Autores y afiliaciones.** Se enriquecieron los top 200 autores más prolíficos con llamadas al endpoint /author/{id}, obteniendo sus afiliaciones institucionales (cuando están disponibles), número total de publicaciones y conteo de citas.

> **Apuntes de implementación.** Se manejaron límites de tasa con backoff y *reintentos selectivos* (de 998→*1000/1000*). El campo venue se maneja como string por restricciones de campos en Graph v1; se reporta el url del paper como enlace principal.

---

## 🔗 Referencias

- **Semantic Scholar API Docs**: https://api.semanticscholar.org/api-docs/graph
- **Schema.org Vocabulary**: https://schema.org/
- **DBLP**: https://dblp.org/
- **FOAF Ontology**: http://xmlns.com/foaf/spec/

---

## 👥 Autores

- **Nombre del Estudiante** - UTPL - Interoperabilidad de Datos (BIM1)

---

## 📄 Licencia

Este proyecto es parte de un trabajo académico para la UTPL.

