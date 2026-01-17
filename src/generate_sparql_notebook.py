import nbformat as nbf
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell

nb = new_notebook()

nb.cells.append(new_markdown_cell("""# 🦁 Consultas SPARQL: Análisis del Grafo de Agricultura de Precisión

Este notebook contiene **15 consultas SPARQL** diseñadas para extraer información del grafo RDF generado previamente (`out/agri_graph.ttl`).

Las consultas cubren:
*   Consultas básicas (SELECT)
*   Filtrado (FILTER, REGEX)
*   Agrupamiento y Agregación (GROUP BY, COUNT, ORDER BY)
*   Property Paths (Búsqueda en profundidad)
*   Subqueries y Lógica condicional
"""))

# Setup Cell
nb.cells.append(new_code_cell("""import pandas as pd
from rdflib import Graph

# Cargar el grafo generado
g = Graph()
g.parse("out/agri_graph.ttl", format="turtle")

print(f"✅ Grafo cargado con {len(g)} triples.")

# Función helper para mostrar resultados en DataFrame
def query_to_df(query):
    results = g.query(query)
    data = []
    for row in results:
        data.append({str(k): str(v) for k, v in row.asdict().items()})
    return pd.DataFrame(data)
"""))

# --- Queries Definition ---

queries = [
    {
        "title": "1. Listar 10 artículos (URI y Título)",
        "desc": "Consulta básica para recuperar identificadores y títulos de artículos.",
        "sparql": """
PREFIX schema: <http://schema.org/>
SELECT ?art ?title
WHERE {
  ?art a schema:Article ;
       schema:title ?title .
}
LIMIT 10
"""
    },
    {
        "title": "2. Autores con 'Smith' en su nombre",
        "desc": "Uso de `FILTER` y `REGEX` para búsqueda de texto.",
        "sparql": """
PREFIX schema: <http://schema.org/>
SELECT ?person ?name
WHERE {
  ?person a schema:Person ;
          schema:name ?name .
  FILTER REGEX(?name, "Smith", "i")
}
LIMIT 10
"""
    },
    {
        "title": "3. Conteo total de artículos y autores",
        "desc": "Uso de `UNION` o conteos separados (aquí usamos UNION implícito al contar tipos distintos en columnas opcionales, o simplemente dos counts). Haremos un conteo de artículos.",
        "sparql": """
PREFIX schema: <http://schema.org/>
SELECT (COUNT(?art) AS ?totalArticles)
WHERE {
  ?art a schema:Article .
}
"""
    },
    {
        "title": "4. Cantidad de artículos por año",
        "desc": "Uso de `GROUP BY` y `ORDER BY`.",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
SELECT ?year (COUNT(?art) AS ?count)
WHERE {
  ?art a schema:Article ;
       schema:datePublished ?date .
  BIND(YEAR(?date) AS ?year)
}
GROUP BY ?year
ORDER BY DESC(?year)
"""
    },
    {
        "title": "5. Top 10 Venues (Revistas/Conferencias) con más publicaciones",
        "desc": "Agrupamiento por entidad relacionada (`schema:isPartOf`).",
        "sparql": """
PREFIX schema: <http://schema.org/>
SELECT ?venueName (COUNT(?art) AS ?count)
WHERE {
  ?art a schema:Article ;
       schema:isPartOf ?venue .
  ?venue schema:name ?venueName .
}
GROUP BY ?venueName
ORDER BY DESC(?count)
LIMIT 10
"""
    },
    {
        "title": "6. Top 10 Conceptos (Topics) más frecuentes",
        "desc": "Análisis de temáticas usando `dct:subject`.",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?conceptLabel (COUNT(?art) AS ?count)
WHERE {
  ?art dct:subject ?concept .
  ?concept skos:prefLabel ?conceptLabel .
}
GROUP BY ?conceptLabel
ORDER BY DESC(?count)
LIMIT 10
"""
    },
    {
        "title": "7. Artículos sobre un tema específico (ej. 'Machine learning')",
        "desc": "Filtrado por concepto específico.",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT ?title
WHERE {
  ?art a schema:Article ;
       schema:title ?title ;
       dct:subject ?concept .
  ?concept skos:prefLabel ?label .
  FILTER (LCASE(?label) = "machine learning")
}
LIMIT 10
"""
    },
    {
        "title": "8. Autores que han publicado sobre 'Remote sensing'",
        "desc": "Navegación de grafo: `Person` <- `author` - `Article` - `subject` -> `Concept`.",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?authorName
WHERE {
  ?art dct:subject ?concept ;
       schema:author ?person .
  ?concept skos:prefLabel ?label .
  ?person schema:name ?authorName .
  FILTER (REGEX(?label, "Remote sensing", "i"))
}
LIMIT 15
"""
    },
    {
        "title": "9. Pares de co-autores (escribieron juntos)",
        "desc": "Self-join: Dos autores distintos que comparten el mismo artículo.",
        "sparql": """
PREFIX schema: <http://schema.org/>

SELECT ?author1 ?author2 (COUNT(?art) as ?collabCount)
WHERE {
  ?art schema:author ?p1 .
  ?art schema:author ?p2 .
  ?p1 schema:name ?author1 .
  ?p2 schema:name ?author2 .
  FILTER (STR(?p1) < STR(?p2)) # Evitar duplicados simétricos (A-B y B-A)
}
GROUP BY ?author1 ?author2
ORDER BY DESC(?collabCount)
LIMIT 10
"""
    },
    {
        "title": "10. Artículos que citan a artículos populares (>10 citas)",
        "desc": "Uso de property paths para citas (`schema:citation`) y filtrado por métrica (asumiendo que cargamos `ex:citationCount`).",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX ex: <http://example.org/agri#>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>

SELECT ?sourceTitle ?citedTitle ?citedCount
WHERE {
  ?source a schema:Article ;
          schema:title ?sourceTitle ;
          schema:citation ?target .
  
  ?target schema:title ?citedTitle ;
          ex:citationCount ?citedCount .
          
  FILTER (?citedCount > 50)
}
LIMIT 10
"""
    },
    {
        "title": "11. Artículos sin DOI",
        "desc": "Uso de `FILTER NOT EXISTS` o `OPTIONAL` + `!BOUND` para encontrar datos faltantes.",
        "sparql": """
PREFIX schema: <http://schema.org/>

SELECT ?title
WHERE {
  ?art a schema:Article ;
       schema:title ?title .
  FILTER NOT EXISTS { ?art schema:doi ?doi }
}
LIMIT 10
"""
    },
    {
        "title": "12. Promedio de citas de los artículos en el grafo",
        "desc": "Agregación global con `AVG`.",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX ex: <http://example.org/agri#>

SELECT (AVG(?cc) AS ?avgCitations)
WHERE {
  ?art a schema:Article ;
       ex:citationCount ?cc .
}
"""
    },
    {
        "title": "13. Autores 'prolíficos' (Más de 5 pappers)",
        "desc": "Subquery o Group By con `HAVING`.",
        "sparql": """
PREFIX schema: <http://schema.org/>

SELECT ?authorName (COUNT(?art) AS ?paperCount)
WHERE {
  ?art schema:author ?person .
  ?person schema:name ?authorName .
}
GROUP BY ?authorName
HAVING (COUNT(?art) > 5)
ORDER BY DESC(?paperCount)
LIMIT 10
"""
    },
    {
        "title": "14. Property Path: Conceptos citados indirectamente",
        "desc": "Artículos que tratan un tema y citan a otro artículo que trata sobre 'Deep learning'. (Cadena: Art(T1) -> cites -> Art(DL)).",
        "sparql": """
PREFIX schema: <http://schema.org/>
PREFIX dct: <http://purl.org/dc/terms/>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>

SELECT DISTINCT ?topicSource
WHERE {
  ?source a schema:Article ;
          dct:subject/skos:prefLabel ?topicSource ;
          schema:citation ?target .
  
  ?target dct:subject/skos:prefLabel ?topicTarget .
  
  FILTER (LCASE(?topicTarget) = "deep learning")
  FILTER (LCASE(?topicSource) != "deep learning")
}
LIMIT 10
"""
    },
    {
        "title": "15. Artículos publicados en conferencias (IEEE/ACM/Proc)",
        "desc": "Filtrado por nombre del venue usando expresiones regulares.",
        "sparql": """
PREFIX schema: <http://schema.org/>

SELECT ?title ?venueName
WHERE {
  ?art schema:isPartOf ?venue ;
       schema:title ?title .
  ?venue schema:name ?venueName .
  FILTER (REGEX(?venueName, "IEEE|Conference|Proceedings|ACM", "i"))
}
LIMIT 10
"""
    }
]

# --- Generate Cells ---

for q in queries:
    # Markdown Header
    nb.cells.append(new_markdown_cell(f"### {q['title']}\n{q['desc']}"))
    
    # Code Cell
    code = f"""query = \"\"\"{q['sparql']}\"\"\"

df = query_to_df(query)
display(df)
"""
    nb.cells.append(new_code_cell(code))
    
# Save notebook
with open("notebooks/02_consultas_sparql.ipynb", "w", encoding="utf-8") as f:
    nbf.write(nb, f)

print("✅ Notebook 'notebooks/02_consultas_sparql.ipynb' generado correctamente.")
