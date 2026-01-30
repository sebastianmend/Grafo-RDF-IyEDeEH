import pandas as pd
import rdflib
from rdflib import Graph, Literal, URIRef, Namespace
from rdflib.namespace import RDF, RDFS, OWL, FOAF, DCTERMS, XSD
import requests
import time
from SPARQLWrapper import SPARQLWrapper, JSON
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import zipfile
import os

# --- Configuration ---
DATA_DIR = r"c:\Users\Usuario\Documents\Universidad\7mo Ciclo\InterOperabilidadYExplotDatos\Bim1InteroperabilidadDatos2B (2) - copia\Bim1InteroperabilidadDatos-main - copia (2) - copia\notebooks\data\processed"
OUT_DIR = r"c:\Users\Usuario\Documents\Universidad\7mo Ciclo\InterOperabilidadYExplotDatos\Bim1InteroperabilidadDatos2B (2) - copia\Bim1InteroperabilidadDatos-main - copia (2) - copia\notebooks\out"
INPUT_TTL = os.path.join(OUT_DIR, "agri_graph_improved.ttl")
OUTPUT_TTL = os.path.join(OUT_DIR, "enriched_graph.ttl")
PAPERS_CSV = os.path.join(DATA_DIR, "papers.csv")
FIELDS_CSV = os.path.join(DATA_DIR, "fields.csv")
ZIP_NAME = "Entregable_Final.zip"

EX = Namespace("http://example.org/agri#")
DBO = Namespace("http://dbpedia.org/ontology/")
DBR = Namespace("http://dbpedia.org/resource/")

def setup_phase():
    print("--- Phase 0: Load & Prep ---")
    # Load Graph
    g = Graph()
    print(f"Loading graph from {INPUT_TTL}...")
    g.parse(INPUT_TTL, format="turtle")
    print(f"Graph loaded with {len(g)} triples.")

    # Load CSVs
    papers_df = pd.read_csv(PAPERS_CSV)
    fields_df = pd.read_csv(FIELDS_CSV)
    
    # Clean Data
    print(f"Papers before cleaning: {len(papers_df)}")
    papers_df = papers_df.dropna(subset=['abstract', 'paperId'])
    papers_df = papers_df[papers_df['abstract'].str.strip() != ""]
    print(f"Papers after cleaning: {len(papers_df)}")
    
    return g, papers_df, fields_df

def entity_linking_phase(g, papers_df, fields_df):
    print("--- Phase A: Entity Linking (Spotlight) ---")
    spotlight_url = "https://api.dbpedia-spotlight.org/en/annotate"
    
    # Process papers (Subset for demo)
    subset_size = 50
    print(f"Annotating first {subset_size} papers...")
    
    count = 0
    for index, row in papers_df.head(subset_size).iterrows():
        abstract = row['abstract']
        paper_id = row['paperId']
        paper_uri = URIRef(f"{EX}art-{str(paper_id)}")
        
        try:
            params = {'text': abstract, 'confidence': 0.5}
            headers = {'Accept': 'application/json'}
            response = requests.get(spotlight_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'Resources' in data:
                    for res in data['Resources']:
                        dbpedia_uri = URIRef(res['@URI'])
                        g.add((paper_uri, URIRef("http://schema.org/mentions"), dbpedia_uri))
            else:
                print(f"Error {response.status_code} for paper {paper_id}")
            
            time.sleep(0.5) # Rate limiting
            
        except Exception as e:
            print(f"Exception for paper {paper_id}: {e}")
        
        count += 1
        if count % 10 == 0:
            print(f"Processed {count}/{subset_size}")

    # Process keywords
    print("Linking keywords...")
    for index, row in fields_df.iterrows():
        field_name = row['fieldName']
        # Create a local concept URI if not strictly defined, assuming standard pattern or use from graph
        # In previous script, concept URIs were constructed. We'll search or assume.
        # Assuming EX[make_id(field_name)] or similar, but let's just make a lookup if possible
        # For this exercise, let's just assume we want to link the string to a DBpedia resource
        # if the graph uses a specific URI for the concept, we should find it.
        # Let's simple use the spotlight to find the URI for the keyword.
        
        try:
            params = {'text': field_name, 'confidence': 0.5}
            headers = {'Accept': 'application/json'}
            response = requests.get(spotlight_url, params=params, headers=headers, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                if 'Resources' in data:
                    # Take the first one which matches best usually
                    dbpedia_uri = URIRef(data['Resources'][0]['@URI'])
                    # We need the local URI for this field. 
                    # Assuming pattern: ex:field-<sanitized_name> from previous knowledge or just search label
                    # Let's search by label in graph
                    
                    query = f"""
                    SELECT ?c WHERE {{
                        ?c a <http://www.w3.org/2004/02/skos/core#Concept> .
                        ?c <http://www.w3.org/2004/02/skos/core#prefLabel> "{field_name}" .
                    }}
                    """
                    res = g.query(query)
                    for r in res:
                        local_concept = r.c
                        g.add((local_concept, OWL.sameAs, dbpedia_uri))
            
            time.sleep(0.2)
        except Exception as e:
            print(f"Error linking field {field_name}: {e}")
            
    print(f"Graph size after linking: {len(g)}")
    return g

def enrichment_phase(g):
    print("--- Phase B: Enrichment (SPARQL Remote) ---")
    
    # Extract unique DBpedia URIs
    dbpedia_uris = set()
    for s, p, o in g.triples((None, URIRef("http://schema.org/mentions"), None)):
        if str(o).startswith("http://dbpedia.org/resource/"):
            dbpedia_uris.add(o)
    for s, p, o in g.triples((None, OWL.sameAs, None)):
        if str(o).startswith("http://dbpedia.org/resource/"):
            dbpedia_uris.add(o)
            
    print(f"Found {len(dbpedia_uris)} unique DBpedia entities to enrich.")
    
    sparql = SPARQLWrapper("http://dbpedia.org/sparql")
    
    uris_list = list(dbpedia_uris)
    batch_size = 50
    
    for i in range(0, len(uris_list), batch_size):
        batch = uris_list[i:i+batch_size]
        values_clause = " ".join([f"<{u}>" for u in batch])
        
        query = f"""
        PREFIX foaf: <http://xmlns.com/foaf/0.1/>
        PREFIX dct: <http://purl.org/dc/terms/>
        PREFIX dbo: <http://dbpedia.org/ontology/>
        
        SELECT ?res ?name ?subject ?abstract WHERE {{
            VALUES ?res {{ {values_clause} }}
            ?res foaf:name ?name .
            OPTIONAL {{ ?res dct:subject ?subject }} .
            OPTIONAL {{ ?res dbo:abstract ?abstract . FILTER(LANG(?abstract) = "en") }}
        }}
        """
        
        try:
            sparql.setQuery(query)
            sparql.setReturnFormat(JSON)
            results = sparql.query().convert()
            
            for result in results["results"]["bindings"]:
                res_uri = URIRef(result["res"]["value"])
                if "name" in result:
                    g.add((res_uri, FOAF.name, Literal(result["name"]["value"])))
                if "subject" in result:
                    g.add((res_uri, DCTERMS.subject, URIRef(result["subject"]["value"])))
                if "abstract" in result:
                    g.add((res_uri, DBO.abstract, Literal(result["abstract"]["value"], lang='en')))
                    
        except Exception as e:
            print(f"SPARQL Error batch {i}: {e}")
            
        print(f"Enriched batch {i//batch_size + 1}")
        
    g.serialize(destination=OUTPUT_TTL, format="turtle")
    print(f"Enriched graph saved to {OUTPUT_TTL}")
    return g

def analysis_phase(g):
    print("--- Phase C: Queries & Visualizations ---")
    
    # Query 1: Top DBpedia Entities
    q1 = """
    PREFIX schema: <http://schema.org/>
    SELECT ?entity (COUNT(?paper) as ?count) WHERE {
        ?paper schema:mentions ?entity .
    } GROUP BY ?entity ORDER BY DESC(?count) LIMIT 10
    """
    
    res1 = g.query(q1)
    entities = []
    counts = []
    for row in res1:
        entities.append(str(row.entity).split('/')[-1])
        counts.append(int(row['count']))
        
    plt.figure(figsize=(10, 6))
    sns.barplot(x=counts, y=entities)
    plt.title("Top 10 Mentioned DBpedia Entities")
    plt.xlabel("Count")
    plt.tight_layout()
    plt.savefig(os.path.join(OUT_DIR, "viz_top_entities.png"))
    print("Generated viz_top_entities.png")

    # Additional queries can be added here as requested in the full prompt
    # For brevity in this verification script, I'll stick to the core flow verification

def package_phase():
    print("--- Phase E: Packaging ---")
    files_to_zip = [
        # Note: In real notebook generation, we'd enable the notebook file itself.
        # Here we zip the resources.
        PAPERS_CSV,
        FIELDS_CSV,
        INPUT_TTL,
        OUTPUT_TTL
    ]
    
    zip_path = os.path.join(OUT_DIR, ZIP_NAME)
    with zipfile.ZipFile(zip_path, 'w') as zf:
        for f in files_to_zip:
            if os.path.exists(f):
                zf.write(f, os.path.basename(f))
    print(f"Created {zip_path}")

if __name__ == "__main__":
    g, papers, fields = setup_phase()
    g = entity_linking_phase(g, papers, fields)
    g = enrichment_phase(g)
    analysis_phase(g)
    package_phase()
