import nbformat as nbf
from pathlib import Path

# Configuración
NOTEBOOK_PATH = Path("notebooks/01_extraccion_precision_agri.ipynb")
SRC_CODE_PATH = Path("src/rdf_generator.py")

# Verificar archivos
if not NOTEBOOK_PATH.exists():
    print(f"❌ Notebook no encontrado: {NOTEBOOK_PATH}")
    exit(1)

# Leer el código fuente mejorado
# Leemos el script pero necesitamos adaptarlo para el notebook
# 1. Eliminar imports de sys y __file__
# 2. Ajustar rutas (En el notebook, CWD es la carpeta del notebook)
rdf_logic = """import pandas as pd
import re
import unicodedata
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from pathlib import Path

# Ajuste de rutas para el Notebook
# Asumiendo que el notebook corre en notebooks/ y data está en notebooks/data
DATA = Path("data/processed")
OUT = Path("out")
OUT.mkdir(parents=True, exist_ok=True)

print(f"📂 Directorio de datos: {DATA.absolute()}")
print(f"📂 Directorio de salida: {OUT.absolute()}")

# Prefijos / Namespaces
EX = Namespace("http://example.org/agri#")
SCHEMA = Namespace("http://schema.org/")
DCT = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")

g = Graph()
g.bind("ex", EX)
g.bind("schema", SCHEMA)
g.bind("dct", DCT)
g.bind("skos", SKOS)
g.bind("rdfs", RDFS)

# --- Utilidades ---
def slugify_safe(text):
    \"\"\"Convierte texto a formato slug seguro para URIs (compatible Python 3).\"\"\"
    if text is None:
        return "unknown"
    # Normalizar unicode
    text = unicodedata.normalize('NFKD', str(text))
    # Convertir a ASCII, ignorar caracteres no ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Convertir a minúsculas
    text = text.lower()
    # Reemplazar caracteres no alfanuméricos por guiones
    text = re.sub(r'[^\\w\\s-]', '', text)
    # Reemplazar espacios y guiones múltiples por un solo guion
    text = re.sub(r'[-\\s]+', '-', text)
    # Eliminar guiones al inicio y final
    text = text.strip('-')
    # Si queda vacío, usar "unknown"
    return text if text else "unknown"

def U(kind, raw_id):
    \"\"\"Crea un URIRef desde un tipo y un ID raw.\"\"\"
    return URIRef(f"{EX}{kind}-{slugify_safe(raw_id)}")

def add_lit(s, p, val, dtype=None):
    \"\"\"Añade un literal si no es NaN.\"\"\"
    if pd.isna(val):
        return
    if dtype:
        g.add((s, p, Literal(val, datatype=dtype)))
    else:
        g.add((s, p, Literal(val)))

# --- Carga CSVs ---
print("📂 Cargando CSVs...")
try:
    papers = pd.read_csv(DATA / "papers.csv")
    authors = pd.read_csv(DATA / "authors.csv")
    venues = pd.read_csv(DATA / "venues.csv")
    fields = pd.read_csv(DATA / "fields.csv")
    pa = pd.read_csv(DATA / "paper_authoredby_author.csv")
    pv = pd.read_csv(DATA / "paper_publishedin_venue.csv")
    pt = pd.read_csv(DATA / "paper_has_topic.csv")
    pc = pd.read_csv(DATA / "paper_cites_paper.csv")
except FileNotFoundError as e:
    print(f"❌ Error al cargar archivos CSV: {e}")
    # En notebook no usamos sys.exit, mejor lanzar error o parar
    raise e

# author_affiliations puede no existir o estar vacío
aff_path = DATA / "author_affiliations.csv"
if aff_path.exists():
    aff = pd.read_csv(aff_path)
    print(f"   Afiliaciones encontradas: {len(aff)} registros")
else:
    aff = pd.DataFrame(columns=["authorId", "affiliation"])
    print("   ⚠️ author_affiliations.csv no encontrado (opcional)")

# Cargar autores enriquecidos si existe
auth_enriched_path = DATA / "authors_enriched.csv"
if auth_enriched_path.exists():
    authors_enriched = pd.read_csv(auth_enriched_path)
    # Merge para tener las métricas en el dataframe principal de autores
    # Usamos how='left' para mantener todos los autores originales
    authors = authors.merge(authors_enriched[['authorId', 'paperCount', 'citationCount']], on='authorId', how='left')
    print(f"   Autores enriquecidos cargados: {len(authors_enriched)} registros")
else:
    print("   ⚠️ authors_enriched.csv no encontrado (métricas de autor no disponibles)")

print(f"   Papers: {len(papers)}, Authors: {len(authors)}, Venues: {len(venues)}, Fields: {len(fields)}")

# --- Papers como schema:Article ---
print("\\n📄 Procesando papers...")
for _, r in papers.iterrows():
    A = U("art", r["paperId"])
    g.add((A, RDF.type, SCHEMA.Article))
    add_lit(A, SCHEMA.identifier, r.get("paperId"))
    add_lit(A, SCHEMA.title, r.get("title"))
    add_lit(A, SCHEMA.description, r.get("abstract"))
    
    if pd.notna(r.get("publicationDate")):
        add_lit(A, SCHEMA.datePublished, r.get("publicationDate"), XSD.date)
    elif pd.notna(r.get("year")): # Fallback al año si no hay fecha completa
        add_lit(A, SCHEMA.datePublished, str(int(r.get("year"))), XSD.gYear)
        
    add_lit(A, SCHEMA.doi, r.get("doi"))
    
    # Métricas de paper (Nuevos campos)
    if pd.notna(r.get("citationCount")):
        add_lit(A, EX.citationCount, int(r.get("citationCount")), XSD.integer)
    if pd.notna(r.get("influentialCitationCount")):
        add_lit(A, EX.influentialCitationCount, int(r.get("influentialCitationCount")), XSD.integer)

    if pd.notna(r.get("url")):
        try:
            g.add((A, SCHEMA.url, URIRef(r["url"])))
        except:
            pass  # Si la URL no es válida, la saltamos

# --- Authors como schema:Person ---
print("👤 Procesando authors...")
for _, r in authors.iterrows():
    P = U("person", r["authorId"])
    g.add((P, RDF.type, SCHEMA.Person))
    add_lit(P, SCHEMA.identifier, r.get("authorId"))
    add_lit(P, SCHEMA.name, r.get("name"))
    
    # Métricas de autor (si existen tras el merge)
    if "paperCount" in r and pd.notna(r.get("paperCount")):
        add_lit(P, EX.paperCount, int(r.get("paperCount")), XSD.integer)
    if "citationCount" in r and pd.notna(r.get("citationCount")):
        add_lit(P, EX.citationCount, int(r.get("citationCount")), XSD.integer)

    if pd.notna(r.get("url")):
        try:
            g.add((P, SCHEMA.url, URIRef(r["url"])))
        except:
            pass

# --- Venues como schema:Periodical ---
print("📚 Procesando venues...")
for _, r in venues.iterrows():
    V = U("periodical", r["venueId"])
    g.add((V, RDF.type, SCHEMA.Periodical))
    add_lit(V, SCHEMA.identifier, r.get("venueId"))
    add_lit(V, SCHEMA.name, r.get("name"))

# --- Fields/Topics como skos:Concept ---
print("🔬 Procesando fields...")
for _, r in fields.iterrows():
    C = U("concept", r["fieldName"])
    g.add((C, RDF.type, SKOS.Concept))
    add_lit(C, SKOS.prefLabel, r.get("fieldName"))

# --- Relaciones: AUTHORED_BY, PUBLISHED_IN, HAS_TOPIC ---
print("🔗 Procesando relaciones...")
for _, r in pa.iterrows():
    A = U("art", r["paperId"])
    P = U("person", r["authorId"])
    g.add((A, SCHEMA.author, P))

for _, r in pv.iterrows():
    A = U("art", r["paperId"])
    V = U("periodical", r["venueId"])
    g.add((A, SCHEMA.isPartOf, V))

for _, r in pt.iterrows():
    A = U("art", r["paperId"])
    C = U("concept", r["fieldName"])  # Usa fieldName, no fieldId
    g.add((A, DCT.subject, C))

# --- CITES ---
print("📎 Procesando citas...")
for _, r in pc.iterrows():
    S = U("art", r["sourcePaperId"])
    T = U("art", r["targetPaperId"])
    g.add((S, SCHEMA.citation, T))
    
    # Asegurar que el target también esté tipado como Article
    # Esto "valida" que la referencia sea un nodo válido en el grafo
    g.add((T, RDF.type, SCHEMA.Article))

# --- Afiliaciones: Organization (simplificado - solo affiliation string) ---
if not aff.empty:
    print("🏢 Procesando afiliaciones...")
    for _, r in aff.iterrows():
        P = U("person", r["authorId"])
        aff_name = r.get("affiliation")
        if pd.notna(aff_name):
            # Crear organización desde el nombre de afiliación
            O = U("org", aff_name)
            g.add((O, RDF.type, SCHEMA.Organization))
            add_lit(O, SCHEMA.name, aff_name)
            g.add((P, SCHEMA.affiliation, O))

# --- Guardar ---
ttl_path = OUT / "agri_graph.ttl"
g.serialize(ttl_path, format="turtle")
print(f"\\n✅ RDF generado: {ttl_path}")
print(f"   Triples: {len(g)}")
print(f"   Tamaño: {ttl_path.stat().st_size / 1024 / 1024:.2f} MB")

# También guardar en formato N-Triples (opcional)
nt_path = OUT / "agri_graph.nt"
g.serialize(nt_path, format="nt")
print(f"✅ N-Triples generado: {nt_path}")
print(f"   Tamaño: {nt_path.stat().st_size / 1024 / 1024:.2f} MB")
"""

# Cargar notebook
nb = nbf.read(NOTEBOOK_PATH, as_version=4)

# Buscar la celda que contiene "rdflib" y "SCHEMA" para reemplazarla
replaced = False
for cell in nb.cells:
    if cell.cell_type == 'code':
        if 'rdflib' in cell.source and 'SCHEMA =' in cell.source and 'to_nodes_edges' not in cell.source:
            print("✅ Celda objetivo encontrada. Actualizando código...")
            cell.source = rdf_logic
            replaced = True
            break

if not replaced:
    print("⚠️ No se encontró la celda específica para reemplazar. Agregando al final... (Revisa manualmente)")
    nb.cells.append(nbf.v4.new_code_cell(rdf_logic))
else:
    print("✅ Notebook actualizado correctamente.")

# Guardar changes
nbf.write(nb, NOTEBOOK_PATH)
print(f"💾 Guardado en: {NOTEBOOK_PATH}")
