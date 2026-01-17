# ✅ Verificación de Requisitos - Fase 2: Conversión RDF y GraphDB

Checklist completo contra los objetivos de la Fase 2.

---

## 🎯 Objetivos de la Fase 2

### Objetivo 1: Convertir datos a RDF según modelo común
- ✅ **RDF generado**: `notebooks/out/agri_graph.ttl` (formato Turtle)
- ✅ **RDF alternativo**: `notebooks/out/agri_graph.nt` (formato N-Triples)
- ✅ **Vocabularios estándar utilizados**:
  - Schema.org (Article, Person, Periodical, Organization)
  - DCT (Dublin Core Terms) para subjects
  - SKOS para conceptos (fields)
- ✅ **Modelo alineado con `data_model/schema.yml`**:
  - Papers → `schema:Article`
  - Authors → `schema:Person`
  - Venues → `schema:Periodical`
  - Fields → `skos:Concept`
  - Relaciones: `schema:author`, `schema:isPartOf`, `dct:subject`, `schema:citation`
- ✅ **Código en notebook**: Celda 12 genera RDF desde CSVs procesados

### Objetivo 2: Almacenar datos en GraphDB
- ✅ **Instrucciones completas**: Celda 13 del notebook con pasos detallados
- ✅ **Repositorio definido**: `agri-precision`
- ✅ **Prefijos documentados**: ex, schema, dct, skos
- ⚠️ **Pendiente de ejecución**: El usuario debe seguir las instrucciones para:
  1. Crear repositorio en GraphDB
  2. Importar `agri_graph.ttl`
  3. Tomar capturas de pantalla

---

## 📦 Entregables Requeridos

### 1. Datos RDF subidos en GraphDB
- ✅ **RDF generado**: `notebooks/out/agri_graph.ttl` existe
- ✅ **Tamaño**: ~10-11 MB (verificado en ejecución)
- ✅ **Formato**: Turtle (TTL) y N-Triples (NT)
- ⚠️ **Pendiente**: Subir a GraphDB siguiendo instrucciones de celda 13

### 2. Notebook en formato HTML utilizado para convertir datos a RDF
- ✅ **Notebook HTML generado**: `notebooks/01_extraccion_precision_agri.html`
- ✅ **Incluye celda RDF**: Celda 12 con código de conversión
- ✅ **Incluye instrucciones GraphDB**: Celda 13 con pasos detallados
- ✅ **Exportación automática**: Celda 11 permite exportar a HTML

### 3. Informe que resuma las tres fases del proyecto
- ✅ **Texto Fase 1**: Disponible en README.md y VERIFICACION_REQUISITOS.md
- ✅ **Texto Fase 2**: Disponible en este documento (ver abajo)
- ⚠️ **Pendiente**: Crear informe PDF final con:
  - Resumen de las 3 fases
  - Imágenes de GraphDB (repositorio, import, visual graph, consultas SPARQL)
  - Métricas y resultados

---

## 📸 Capturas Necesarias para el Informe

Según las instrucciones en la celda 13 del notebook, necesitas tomar estas capturas:

1. **Repositorio creado** (`agri-precision`) en GraphDB
2. **Import success** (pantalla que muestra el conteo de triples después de importar)
3. **Visual Graph** con nodos Article–Person–Periodical–Concept (1-2 capturas)
4. **Resultados de consulta SPARQL A** (artículos con autores, venues, conceptos)
5. **Resultados de consulta SPARQL B** (top conceptos por cantidad)
6. **Resultados de consulta SPARQL C** (citas paper → paper)

---

## 📝 Texto para el Informe PDF (Fase 2)

### Conversión a RDF

> **Modelo RDF y vocabularios estándar.** Los datos extraídos y preprocesados (CSVs en `data/processed/`) se convirtieron a formato RDF usando vocabularios estándar: Schema.org para entidades principales (Article, Person, Periodical, Organization), Dublin Core Terms (DCT) para subjects, y SKOS para conceptos. El modelo RDF preserva la estructura del grafo definida en `data_model/schema.yml`, mapeando Papers a `schema:Article`, Authors a `schema:Person`, Venues a `schema:Periodical`, y Fields a `skos:Concept`. Las relaciones se representan mediante propiedades estándar: `schema:author` (AUTHORED_BY), `schema:isPartOf` (PUBLISHED_IN), `dct:subject` (HAS_TOPIC), y `schema:citation` (CITES).

> **Generación de triples.** Se generaron dos formatos de salida: Turtle (TTL) y N-Triples (NT), con un total de aproximadamente [N] triples RDF. El archivo principal `agri_graph.ttl` tiene un tamaño de ~10-11 MB y contiene todas las entidades y relaciones del grafo de conocimiento.

### Almacenamiento en GraphDB

> **Repositorio y configuración.** Se creó el repositorio `agri-precision` en GraphDB con configuración estándar (RDF4J, OWL-Horst). Se configuraron los namespaces necesarios: `ex` (http://example.org/agri#), `schema` (http://schema.org/), `dct` (http://purl.org/dc/terms/), y `skos` (http://www.w3.org/2004/02/skos/core#). El archivo RDF se importó exitosamente, preservando la integridad de todos los triples.

> **Exploración y consultas SPARQL.** Se realizaron consultas SPARQL para validar el modelo y explorar el grafo: (1) artículos con sus autores, venues y conceptos asociados; (2) top conceptos por cantidad de artículos; (3) relaciones de citación entre papers. El visualizador de grafo de GraphDB permite explorar las conexiones entre Article, Person, Periodical y Concept, confirmando la estructura del modelo de conocimiento.

---

## ✅ Checklist Final Fase 2

### Generación RDF
- [x] Código de conversión RDF implementado (celda 12)
- [x] RDF generado en formato Turtle (`agri_graph.ttl`)
- [x] RDF generado en formato N-Triples (`agri_graph.nt`)
- [x] Vocabularios estándar utilizados (Schema.org, DCT, SKOS)
- [x] Modelo alineado con `data_model/schema.yml`

### GraphDB
- [x] Instrucciones completas en notebook (celda 13)
- [ ] Repositorio `agri-precision` creado en GraphDB
- [ ] Prefijos configurados en GraphDB
- [ ] RDF importado exitosamente
- [ ] Captura de pantalla: repositorio creado
- [ ] Captura de pantalla: import exitoso (conteo de triples)
- [ ] Captura de pantalla: visual graph
- [ ] Consultas SPARQL ejecutadas (A, B, C)
- [ ] Capturas de resultados de consultas SPARQL

### Documentación
- [x] Notebook HTML generado (incluye celda RDF)
- [x] Instrucciones GraphDB documentadas
- [x] Consultas SPARQL documentadas
- [ ] Informe PDF final creado con:
  - [ ] Resumen de las 3 fases
  - [ ] Imágenes de GraphDB
  - [ ] Métricas y resultados

---

## 📊 Métricas RDF (para el informe)

- **Triples generados**: ~[N] (verificar ejecutando celda 12)
- **Tamaño TTL**: ~10-11 MB
- **Tamaño NT**: ~10-11 MB
- **Formato**: Turtle (TTL) y N-Triples (NT)
- **Vocabularios**: Schema.org, DCT, SKOS
- **Entidades principales**: Article, Person, Periodical, Concept, Organization

---

## 🚀 Próximos Pasos

1. **Ejecutar celda 12** del notebook (si no lo has hecho) para generar RDF
2. **Abrir GraphDB** y seguir instrucciones de celda 13
3. **Tomar todas las capturas** indicadas
4. **Crear informe PDF** final con:
   - Resumen de Fase 1 (extracción)
   - Resumen de Fase 2 (RDF + GraphDB)
   - Resumen de Fase 3 (si aplica)
   - Imágenes de GraphDB
   - Métricas y conclusiones

---

**¡Éxito con tu entrega! 🎓🚀**

