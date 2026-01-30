
import rdflib
from rdflib import Graph, Namespace
import os

# Paths
BASE_DIR = "." # Assuming running from project root
graph_path = os.path.join(BASE_DIR, "notebooks/out/enriched_graph.ttl")

print(f"Loading graph from {graph_path}...")
g = Graph()
g.parse(graph_path, format="turtle")
print(f"Graph loaded with {len(g)} triples.")

EX = Namespace("http://example.org/agri#")

# Q1
q1 = """
PREFIX schema: <http://schema.org/>
SELECT ?entity (COUNT(?paper) as ?mentionCount) WHERE {
    ?paper schema:mentions ?entity .
} GROUP BY ?entity ORDER BY DESC(?mentionCount) LIMIT 10
"""
print("\n--- Q1: Top 10 Entities ---")
for row in g.query(q1):
    print(f"{row.mentionCount} - {str(row.entity).split('/')[-1]}")

# Q2
# Relaxed: Top citations that mention ANY entity (removed specific keyword filter)
# Uses OPTIONAL for name to handle cases where enrichment didn't capture the name
q2_strict = """
PREFIX schema: <http://schema.org/>
PREFIX ex: <http://example.org/agri#>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>

SELECT ?title ?cites ?entityName WHERE {
    ?paper a schema:Article ;
           schema:title ?title ;
           ex:citationCount ?cites ;
           schema:mentions ?entity .
    OPTIONAL { ?entity foaf:name ?n }
    BIND(COALESCE(?n, STR(?entity)) AS ?entityName)
    FILTER(?cites > 0)
} ORDER BY DESC(?cites) LIMIT 5
"""
print("\n--- Q2: Impact Papers (Any Enriched Topic) ---")
for row in g.query(q2_strict):
    print(f"[{row.cites}] {str(row.title)[:30]}... -> {row.entityName}")

# Q3
q3 = """
PREFIX schema: <http://schema.org/>
SELECT ?e1 ?e2 (COUNT(?paper) as ?coCount) WHERE {
    ?paper schema:mentions ?e1 .
    ?paper schema:mentions ?e2 .
    FILTER(STR(?e1) < STR(?e2))
} GROUP BY ?e1 ?e2 ORDER BY DESC(?coCount) LIMIT 5
"""
print("\n--- Q3: Co-occurrence ---")
for row in g.query(q3):
    print(f"{row.coCount}: {str(row.e1).split('/')[-1]} <-> {str(row.e2).split('/')[-1]}")

# Q4
# Fixed: Use schema:name instead of foaf:name for Authors
q4 = """
PREFIX schema: <http://schema.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?authorName (COUNT(DISTINCT ?entity) as ?topicCount) WHERE {
    ?paper schema:author ?author .
    ?author schema:name ?authorName . 
    ?paper schema:mentions ?entity .
} GROUP BY ?authorName ORDER BY DESC(?topicCount) LIMIT 5
"""
print("\n--- Q4: Polymath Authors ---")
for row in g.query(q4):
    print(f"{row.topicCount} topics - {row.authorName}")

# Q5
q5 = """
PREFIX owl: <http://www.w3.org/2002/07/owl#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
SELECT ?label ?dbpediaURI WHERE {
    ?c a skos:Concept ;
       skos:prefLabel ?label ;
       owl:sameAs ?dbpediaURI .
} LIMIT 5
"""
print("\n--- Q5: Keyword Validation ---")
for row in g.query(q5):
    print(f"{row.label} -> {row.dbpediaURI}")
