# ✅ Verificación de Requisitos - Fase 1

Checklist completo contra los requisitos del audio de la profesora y el texto del usuario.

---

## 📊 Requisitos Esenciales

| # | Requisito | Estado | Evidencia |
|---|-----------|--------|-----------|
| 1 | **1,000 papers semilla** (rango 500-1,000; máx 5,000) | ✅ | Celda 6 del notebook: "1000 / 1000" |
| 2 | **Enriquecimiento por ID**: venue | ✅ | `FIELDS_DETAILS` incluye `venue` (celda 2) |
| 3 | **Enriquecimiento por ID**: publicationTypes | ✅ | `FIELDS_DETAILS` incluye `publicationTypes` |
| 4 | **Enriquecimiento por ID**: citationCount | ✅ | `FIELDS_DETAILS` incluye `citationCount` |
| 5 | **Enriquecimiento por ID**: influentialCitationCount | ✅ | `FIELDS_DETAILS` incluye `influentialCitationCount` |
| 6 | **Enriquecimiento por ID**: externalIds.DOI | ✅ | `FIELDS_DETAILS` incluye `externalIds` (procesado como `doi`) |
| 7 | **Enriquecimiento por ID**: url | ✅ | `FIELDS_DETAILS` incluye `url` |
| 8 | **Enriquecimiento por ID**: authors | ✅ | `FIELDS_DETAILS` incluye `authors` |
| 9 | **Enriquecimiento por ID**: references.paperId | ✅ | `FIELDS_DETAILS` incluye `references.paperId` |
| 10 | **Grafo CITES construido** | ✅ | Celda 7: `to_nodes_edges()` genera `paper_cites_paper.csv` |
| 11 | **Sin self-edges en CITES** | ✅ | Celda 9: "Self-edges: 0" |
| 12 | **Sin duplicados en CITES** | ✅ | Celda 9: "Duplicados: 0" |
| 13 | **Stubs para referencias externas** | ✅ | Celda 7: "Stubs añadidos: 5772" |
| 14 | **Targets fuera de nodos = 0** | ✅ | Celda 9: "Targets fuera de nodos: 0" |
| 15 | **Filtro API: query** | ✅ | Celda 2: `QUERY = "precision agriculture"` |
| 16 | **Filtro API: year** | ✅ | Celda 2: `YEAR = "2010-"` |
| 17 | **Filtro API: publicationTypes** | ✅ | Celda 2: `PUB_TYPES = "JournalArticle,Conference,..."` |
| 18 | **Filtro API: sort** | ✅ | Celda 2: `SORT = "publicationDate"` |
| 19 | **Filtro API: paginación con token** | ✅ | `etl.py` / `search_until_target()` usa `token` |
| 20 | **Resumen: distribución por año** | ✅ | Celda 8: gráfica "Publicaciones por año" |
| 21 | **Resumen: top venues** | ✅ | Celda 8: tabla y gráfica "Top 10 venues" |
| 22 | **Resumen: top autores** | ✅ | Celda 8: tabla y gráfica "Top 10 autores" |
| 23 | **Resumen: top por influentialCitationCount** | ✅ | Celda 8 y 9: tabla "Top papers influyentes" |
| 24 | **Celdas de diagnóstico** | ✅ | Celda 9: cobertura, campos clave, grafo CITES, conectividad |
| 25 | **Backoff y reintentos** | ✅ | Celda 6: pasada de retry (998 → 1000/1000) |
| 26 | **CSVs en data/processed/** | ✅ | 10 archivos CSV generados (ver README.md) |
| 27 | **Esquema declarado** | ✅ | `data_model/schema.yml` |
| 28 | **Autores con organizaciones** | ✅ | Celda 10: enriquecimiento de top 200 autores con afiliaciones |

---

## 🔧 Retoques Implementados

| # | Retoque | Estado | Implementación |
|---|---------|--------|----------------|
| 1 | **Afiliaciones de autores** | ✅ | Celda 10: llamadas a `/author/{id}` para top 200 autores → `author_affiliations.csv` y `authors_enriched.csv` |
| 2 | **Venue URL documentado** | ✅ | Campo `url` del paper está incluido; documentado en README.md y celda 11 (markdown) |
| 3 | **Exportar notebook a HTML** | ✅ | Instrucciones completas en celda 11 del notebook y README.md |
| 4 | **README.md completo** | ✅ | Creado con: filtros API, cómo correr, dónde están los CSV, texto para el PDF |

---

## 📝 Texto para el Informe PDF

El texto listo para copiar está en **3 lugares** para tu comodidad:

1. **Celda 11 del notebook** (markdown): sección "📝 Texto para el Informe PDF"
2. **README.md**: sección "📝 Texto para el Informe PDF (Fase 1)"
3. **Este archivo**: ver abajo

### Texto Completo

> **Cobertura y enriquecimiento.** Se recolectaron *1,000* publicaciones semilla desde *Semantic Scholar* (Graph API /paper/search/bulk) con la consulta "precision agriculture", filtros year=2010-, publicationTypes=JournalArticle,Conference,Review,Proceedings,Survey, y orden publicationDate. Para cada publicación se consultó /paper/{id} con fields específicos: venue (string), publicationTypes, citationCount, influentialCitationCount, externalIds.DOI, url, authors y references.paperId.

> **Grafo de citación.** A partir de references.paperId se generó la relación *CITES* (paper → paper citado), eliminando auto-citas y duplicados. Se incorporaron *nodos stub* para referencias externas no presentes en el conjunto base, con lo cual se preservan todas las conexiones.

> **Modelo de datos y reuso de vocabulario.** Nodos: Paper, Author, Venue, Field; relaciones: *AUTHORED_BY* (≈schema:author), *PUBLISHED_IN* (≈schema:isPartOf), *HAS_TOPIC* (≈schema:about), *CITES* (≈schema:citation).

> **Exploración y métricas.** Se incluyen la distribución temporal, top venues, top autores y un ranking por influentialCitationCount; además, métricas de conectividad del grafo (porcentaje de papers que citan y que son citados).

> **Autores y afiliaciones.** Se enriquecieron los top 200 autores más prolíficos con llamadas al endpoint /author/{id}, obteniendo sus afiliaciones institucionales (cuando están disponibles), número total de publicaciones y conteo de citas.

> **Apuntes de implementación.** Se manejaron límites de tasa con backoff y *reintentos selectivos* (de 998→*1000/1000*). El campo venue se maneja como string por restricciones de campos en Graph v1; se reporta el url del paper como enlace principal.

---

## 📦 Archivos del Entregable

### Para subir al campus virtual:

1. **Código**:
   - ✅ `notebooks/01_extraccion_precision_agri.ipynb` (notebook original)
   - ✅ `notebooks/01_extraccion_precision_agri.html` (exportar antes de entregar - ver instrucciones en celda 11)
   - ✅ `src/` (directorio completo con `config.py`, `etl.py`, `semanticscholar_client.py`)

2. **Datos**:
   - ✅ `data/processed/` (10 CSVs: papers, authors, venues, fields, relaciones, afiliaciones)
   - ⚠️ `data/raw/` (opcional; pesa mucho si incluyes los 1000+ JSONs)

3. **Modelo**:
   - ✅ `data_model/schema.yml` (esquema del grafo)

4. **Documentación**:
   - ✅ `README.md` (este archivo - instrucciones completas)
   - ✅ `VERIFICACION_REQUISITOS.md` (este checklist)

5. **Configuración**:
   - ✅ `requirements.txt` (dependencias)
   - ⚠️ `.env` (NO INCLUIR - es tu API key privada)

---

## 🎯 Checklist Final Antes de Entregar

- [ ] **Ejecutar el notebook completo** (Runtime → Run All)
- [ ] **Exportar a HTML** - ⭐ **NUEVO:** Ejecuta la celda 13 del notebook para exportación automática
- [ ] **Verificar que existen 10 CSVs** en `data/processed/`:
  - [ ] papers.csv
  - [ ] authors.csv
  - [ ] venues.csv
  - [ ] fields.csv
  - [ ] paper_authoredby_author.csv
  - [ ] paper_publishedin_venue.csv
  - [ ] paper_has_topic.csv
  - [ ] paper_cites_paper.csv
  - [ ] author_affiliations.csv
  - [ ] authors_enriched.csv
- [ ] **Verificar que el HTML tiene gráficas** (abrir en navegador)
- [ ] **Copiar texto del informe** (desde celda 11 o README.md)
- [ ] **Comprimir en ZIP** (excluir `.env` y opcionalmente `data/raw/`)
- [ ] **Subir al campus virtual**

---

## 📊 Métricas Finales (para el informe)

Usa estos números en tu PDF:

- **Papers semilla**: 1,000
- **Papers totales (con stubs)**: 6,772
- **Autores**: 3,405
- **Venues**: 446
- **Campos de estudio**: 17
- **Relaciones CITES**: 6,328 (sin self-edges, sin duplicados)
- **Relaciones AUTHORED_BY**: 3,826
- **Relaciones PUBLISHED_IN**: 786
- **Relaciones HAS_TOPIC**: 1,349
- **Autores enriquecidos con afiliaciones**: 200 (top autores)
- **Cobertura temporal**: 2010-presente
- **Tipos de documento**: JournalArticle, Conference, Review, Proceedings, Survey
- **Tasa de éxito en descarga**: 100% (1000/1000 tras reintentos)

---

## ✅ Resumen Ejecutivo

**Todo está listo para entregar.**

Has cumplido:
- ✅ Todos los requisitos esenciales del audio de la profesora
- ✅ Los 3 retoques mínimos recomendados
- ✅ Código bien organizado con módulos reutilizables
- ✅ Documentación completa (README + checklist)
- ✅ Texto listo para copiar al PDF
- ✅ CSVs exportados con esquema declarado
- ✅ Instrucciones para exportar a HTML

**Próximo paso**: Ejecuta el notebook completo una última vez, exporta a HTML, y comprímelo todo (excepto `.env`) para subir al campus.

---

**¡Éxito con tu entrega! 🎓🚀**

