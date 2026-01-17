import pandas as pd
import re
import unicodedata
from rdflib import Graph, Namespace, URIRef, Literal
from rdflib.namespace import RDF, RDFS, XSD
from pathlib import Path

# Configuración de Paths
# Asumimos que el script se corre desde notebooks/ o desde root pero ajustamos
BASE_DIR = Path(__file__).parent if "__file__" in globals() else Path.cwd()
if (BASE_DIR / "data").exists():
    DATA = BASE_DIR / "data/processed"
    OUT = BASE_DIR / "out"
elif (BASE_DIR.parent / "data").exists():
    DATA = BASE_DIR.parent / "data/processed"
    OUT = BASE_DIR.parent / "notebooks/out"
else:
    # Intento fallback
    DATA = Path("data/processed")
    OUT = Path("out")

OUT.mkdir(exist_ok=True, parents=True)

print(f"📂 Usando datos desde: {DATA.absolute()}")
print(f"📂 Guardando RDF en: {OUT.absolute()}")

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
    """Convierte texto a formato slug seguro para URIs (compatible Python 3)."""
    if text is None:
        return "unknown"
    # Normalizar unicode
    text = unicodedata.normalize('NFKD', str(text))
    # Convertir a ASCII, ignorar caracteres no ASCII
    text = text.encode('ascii', 'ignore').decode('ascii')
    # Convertir a minúsculas
    text = text.lower()
    # Reemplazar caracteres no alfanuméricos por guiones
    text = re.sub(r'[^\w\s-]', '', text)
    # Reemplazar espacios y guiones múltiples por un solo guion
    text = re.sub(r'[-\s]+', '-', text)
    # Eliminar guiones al inicio y final
    text = text.strip('-')
    # Si queda vacío, usar "unknown"
    return text if text else "unknown"

def U(kind, raw_id):
    """Crea un URIRef desde un tipo y un ID raw."""
    return URIRef(f"{EX}{kind}-{slugify_safe(raw_id)}")

def add_lit(s, p, val, dtype=None):
    """Añade un literal si no es NaN."""
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
    venues = pd.read_csv(DATA / "venues.csv")
    fields = pd.read_csv(DATA / "fields.csv")
    pa = pd.read_csv(DATA / "paper_authoredby_author.csv")
    pv = pd.read_csv(DATA / "paper_publishedin_venue.csv")
    pt = pd.read_csv(DATA / "paper_has_topic.csv")
    pc = pd.read_csv(DATA / "paper_cites_paper.csv")
except Exception as e:
    print(f"❌ Error cargando CSVs básicos: {e}")
    exit(1)

# Preferir authors_enriched.csv si existe para tener métricas
enriched_path = DATA / "authors_enriched.csv"
if enriched_path.exists():
    print("   ✅ Usando authors_enriched.csv (con métricas)")
    authors = pd.read_csv(enriched_path)
else:
    print("   ℹ️ Usando authors.csv estándar")
    authors = pd.read_csv(DATA / "authors.csv")

# author_affiliations
aff_path = DATA / "author_affiliations.csv"
if aff_path.exists():
    aff = pd.read_csv(aff_path)
    print(f"   Afiliaciones encontradas: {len(aff)} registros")
else:
    aff = pd.DataFrame(columns=["authorId", "affiliation"])
    print("   ⚠️ author_affiliations.csv no encontrado (opcional)")

print(f"   Stats: Papers={len(papers)}, Authors={len(authors)}, Venues={len(venues)}, Fields={len(fields)}")

# --- Papers como schema:Article ---
print("\n📄 Procesando papers...")
for _, r in papers.iterrows():
    A = U("art", r["paperId"])
    g.add((A, RDF.type, SCHEMA.Article))
    add_lit(A, SCHEMA.identifier, r.get("paperId"))
    
    # Título y Label (Mejora 1: Stubs visibles)
    title = r.get("title")
    if pd.notna(title):
        add_lit(A, SCHEMA.title, title)
        add_lit(A, RDFS.label, title) # Label visual
    else:
        # Es un Stub -> Poner label genérico para que se vea en GraphDB
        stub_label = f"Reference {str(r.get('paperId'))[:8]}..."
        add_lit(A, RDFS.label, stub_label)
    
    add_lit(A, SCHEMA.description, r.get("abstract"))
    if pd.notna(r.get("publicationDate")):
        add_lit(A, SCHEMA.datePublished, r.get("publicationDate"), XSD.date)
    add_lit(A, SCHEMA.doi, r.get("doi"))
    
    # Métricas de Papers (Mejora 2: Métricas)
    add_lit(A, EX.citationCount, r.get("citationCount"), XSD.integer)
    add_lit(A, EX.influentialCitationCount, r.get("influentialCitationCount"), XSD.integer)

    if pd.notna(r.get("url")):
        try:
            g.add((A, SCHEMA.url, URIRef(r["url"])))
        except:
            pass 

# --- Authors como schema:Person ---
print("👤 Procesando authors...")
for _, r in authors.iterrows():
    P = U("person", r["authorId"])
    g.add((P, RDF.type, SCHEMA.Person))
    add_lit(P, SCHEMA.identifier, r.get("authorId"))
    add_lit(P, SCHEMA.name, r.get("name"))
    add_lit(P, RDFS.label, r.get("name"))
    
    # Métricas de Autores (Mejora 2: Métricas)
    add_lit(P, EX.paperCount, r.get("paperCount"), XSD.integer)
    add_lit(P, EX.citationCount, r.get("citationCount"), XSD.integer)
    
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
    add_lit(V, RDFS.label, r.get("name"))

# --- Fields/Topics como skos:Concept ---
print("🔬 Procesando fields...")
for _, r in fields.iterrows():
    C = U("concept", r["fieldName"])
    g.add((C, RDF.type, SKOS.Concept))
    add_lit(C, SKOS.prefLabel, r.get("fieldName"))
    add_lit(C, RDFS.label, r.get("fieldName"))

# --- Relaciones ---
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
    C = U("concept", r["fieldName"])
    g.add((A, DCT.subject, C))

print("📎 Procesando citas...")
for _, r in pc.iterrows():
    S = U("art", r["sourcePaperId"])
    T = U("art", r["targetPaperId"])
    g.add((S, SCHEMA.citation, T))

# --- Afiliaciones ---
if not aff.empty:
    print("🏢 Procesando afiliaciones...")
    for _, r in aff.iterrows():
        P = U("person", r["authorId"])
        aff_name = r.get("affiliation")
        if pd.notna(aff_name):
            O = U("org", aff_name)
            g.add((O, RDF.type, SCHEMA.Organization))
            add_lit(O, SCHEMA.name, aff_name)
            add_lit(O, RDFS.label, aff_name)
            g.add((P, SCHEMA.affiliation, O))

# --- Guardar ---
ttl_path = OUT / "agri_graph_improved.ttl"
print(f"💾 Guardando Turtle en {ttl_path} ...")
g.serialize(ttl_path, format="turtle")

print(f"\n✅ RDF MEJORADO generado exitosamente: {ttl_path}")
print(f"   Triples: {len(g)}")
print(f"   Tamaño: {ttl_path.stat().st_size / 1024 / 1024:.2f} MB")
print("   Cambios aplicados: Etiquetas para stubs, Métricas de papers y autores.")
