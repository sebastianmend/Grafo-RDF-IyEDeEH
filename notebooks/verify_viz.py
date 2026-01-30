
import pandas as pd
import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import os

# Setup
BASE_DIR = "."
OUT_DIR = os.path.join(BASE_DIR, "notebooks/out")
if not os.path.exists(OUT_DIR):
    os.makedirs(OUT_DIR)
    
INPUT_TTL = os.path.join(OUT_DIR, "enriched_graph.ttl")

print(f"Loading graph from {INPUT_TTL}...")
g = Graph()
g.parse(INPUT_TTL, format="turtle")
print(f"Graph loaded: {len(g)} triples")

sns.set_theme(style="whitegrid")

# --- Q1 & Viz 1: Bar Chart ---
print("Generating Viz 1...")
q1 = """
PREFIX schema: <http://schema.org/>
SELECT ?entity (COUNT(?paper) as ?mentionCount) WHERE {
    ?paper schema:mentions ?entity .
} GROUP BY ?entity ORDER BY DESC(?mentionCount) LIMIT 10
"""
res = g.query(q1)
data = []
for row in res:
    data.append({"Entity": str(row.entity).split('/')[-1], "Count": int(row.mentionCount)})
df_viz = pd.DataFrame(data)

if not df_viz.empty:
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_viz, x="Count", y="Entity", palette="viridis")
    plt.title("Top 10 Entidades de DBpedia")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "verify_viz_1.png"))
    plt.close()
    print("✅ Viz 1 Saved")
else:
    print("❌ Viz 1 Failed: No Data")

# --- Viz 2: Pie Chart ---
print("Generating Viz 2...")
q_sub = """
PREFIX dct: <http://purl.org/dc/terms/>
SELECT ?subject (COUNT(?s) as ?subjCount) WHERE {
    ?s dct:subject ?subject .
} GROUP BY ?subject ORDER BY DESC(?subjCount) LIMIT 8
"""
res_sub = g.query(q_sub)
labels = [str(r.subject).split(':')[-1] for r in res_sub]
sizes = [int(r.subjCount) for r in res_sub]

if sizes:
    plt.figure(figsize=(8, 8))
    plt.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=140)
    plt.title("Top Categorías")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "verify_viz_2.png"))
    plt.close()
    print("✅ Viz 2 Saved")
else:
    print("❌ Viz 2 Failed: No Data")

# --- Viz 3: Scatter ---
print("Generating Viz 3...")
q_scatter = """
PREFIX schema: <http://schema.org/>
PREFIX ex: <http://example.org/agri#>
SELECT ?paper (SAMPLE(?cites) as ?citationCount) (COUNT(?entity) as ?mentionCount) WHERE {
    ?paper a schema:Article ;
           ex:citationCount ?cites ;
           schema:mentions ?entity .
} GROUP BY ?paper LIMIT 100
"""
res_scatter = g.query(q_scatter)
data_scatter = [{"Cites": float(r.citationCount), "Mentions": int(r.mentionCount)} for r in res_scatter]
df_scatter = pd.DataFrame(data_scatter)

if not df_scatter.empty:
    plt.figure(figsize=(8, 6))
    sns.scatterplot(data=df_scatter, x="Mentions", y="Cites", color="blue", alpha=0.6)
    plt.title("Relación: Cantidad de Entidades vs Citas")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "verify_viz_3.png"))
    plt.close()
    print("✅ Viz 3 Saved")
else:
    print("❌ Viz 3 Failed: No Data")

# --- Viz 4: Network ---
print("Generating Viz 4...")
q3 = """
PREFIX schema: <http://schema.org/>
SELECT ?e1 ?e2 (COUNT(?paper) as ?coCount) WHERE {
    ?paper schema:mentions ?e1 .
    ?paper schema:mentions ?e2 .
    FILTER(STR(?e1) < STR(?e2))
} GROUP BY ?e1 ?e2 ORDER BY DESC(?coCount) LIMIT 15
"""
res_q3 = g.query(q3)
G = nx.Graph()
has_edges = False
for row in res_q3:
    e1 = str(row.e1).split('/')[-1]
    e2 = str(row.e2).split('/')[-1]
    w = int(row.coCount)
    G.add_edge(e1, e2, weight=w)
    has_edges = True

if has_edges:
    plt.figure(figsize=(10, 8))
    pos = nx.spring_layout(G, k=0.5)
    nx.draw(G, pos, with_labels=True, node_color='skyblue', node_size=1500, font_size=10, edge_color='gray')
    plt.title("Red de Co-ocurrencia")
    plt.savefig(os.path.join(OUT_DIR, "verify_viz_4.png"))
    plt.close()
    print("✅ Viz 4 Saved")
else:
    print("❌ Viz 4 Failed: No Data")

# --- Viz 5: Horizontal Bar ---
print("Generating Viz 5...")
q4 = """
PREFIX schema: <http://schema.org/>
PREFIX foaf: <http://xmlns.com/foaf/0.1/>
SELECT ?authorName (COUNT(DISTINCT ?entity) as ?topicCount) WHERE {
    ?paper schema:author ?author .
    ?author schema:name ?authorName .
    ?paper schema:mentions ?entity .
} GROUP BY ?authorName ORDER BY DESC(?topicCount) LIMIT 10
"""
res_q4 = g.query(q4)
data_auth = [{"Author": str(r.authorName), "Topics": int(r.topicCount)} for r in res_q4]
df_auth = pd.DataFrame(data_auth)

if not df_auth.empty:
    plt.figure(figsize=(10, 6))
    sns.barplot(data=df_auth, x="Topics", y="Author", palette="magma")
    plt.title("Top Autores por Diversidad")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "verify_viz_5.png"))
    plt.close()
    print("✅ Viz 5 Saved")
else:
    print("❌ Viz 5 Failed: No Data")
