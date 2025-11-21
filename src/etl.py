from pathlib import Path
import json
import pandas as pd
from tqdm import tqdm
from .semanticscholar_client import SemanticScholarClient

RAW = Path("data/raw")
RAW.mkdir(parents=True, exist_ok=True)
PROC = Path("data/processed")
PROC.mkdir(parents=True, exist_ok=True)


def save_json(obj, path):
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding='utf-8')


def accumulate_bulk_results(client, query, year, publication_types, fields, sort=None, max_pages=10):
    """Itera por 'token' y acumula resultados de /paper/search/bulk."""
    token = None
    all_items = []
    for _ in range(max_pages):
        r = client.search_papers_bulk(query, fields, year, publication_types, sort, token)
        if r.status_code != 200 or not isinstance(r.data, dict):
            break
        data = r.data.get("data", [])
        all_items.extend(data)
        save_json(r.data, RAW / f"search_page_{len(all_items)}.json")
        token = r.data.get("token")
        if not token:
            break
    return all_items


def search_until_target(client, query, year, publication_types, fields, sort=None, target=900, max_pages=30):
    """Búsqueda paginada hasta alcanzar un objetivo de papers, deduplicando por paperId."""
    token = None
    all_rows = []
    seen = set()
    pages = 0
    
    print(f"🔍 Iniciando búsqueda: target={target}, max_pages={max_pages}")
    print(f"   Query: {query[:80]}...")
    print(f"   Year: {year}, Types: {publication_types}")
    
    while pages < max_pages and len(all_rows) < target:
        r = client.search_papers_bulk(query, fields, year, publication_types, sort, token)
        
        if r.status_code != 200 or not isinstance(r.data, dict):
            print(f"⚠️ Error: status={r.status_code}, error={r.error}")
            if r.status_code == 429:
                print("   Rate limit alcanzado. Esperando...")
            elif r.status_code == 400:
                print("   Error 400: Query o parámetros inválidos. Revisa el query.")
            # Guardar respuesta de error para debugging
            if isinstance(r.data, dict):
                save_json(r.data, RAW / f"error_page_{pages + 1}.json")
            break
        
        data = r.data.get("data", [])
        total_found = r.data.get("total", "N/A")
        token = r.data.get("token")
        
        print(f"   Página {pages + 1}: {len(data)} papers recibidos, {len(all_rows)} únicos acumulados")
        if total_found != "N/A":
            print(f"   Total encontrado por API: {total_found}")
        
        if len(data) == 0:
            print("   No hay más resultados disponibles")
            break
        
        new_count = 0
        for it in data:
            pid = it.get("paperId")
            if pid and pid not in seen:
                seen.add(pid)
                new_count += 1
                all_rows.append({
                    "paperId": pid,
                    "title": it.get("title"),
                    "year": it.get("year"),
                    "publicationDate": it.get("publicationDate"),
                    "citationCount": it.get("citationCount"),
                    "publicationTypes": ",".join(it.get("publicationTypes", []) if it.get("publicationTypes") else []),
                    "url": it.get("url"),
                    "openAccessPdf": (it.get("openAccessPdf") or {}).get("url") if isinstance(it.get("openAccessPdf"), dict) else None,
                })
        
        if new_count < len(data):
            print(f"   ⚠️ {len(data) - new_count} duplicados ignorados")
        
        # Guardar página
        save_json(r.data, RAW / f"search_page_{len(all_rows)}.json")
        
        pages += 1
        
        if not token:
            print("   No hay más páginas (token vacío)")
            break
    
    print(f"✅ Búsqueda completada: {len(all_rows)} papers únicos obtenidos en {pages} páginas")
    return pd.DataFrame(all_rows)


def normalize_search_rows(items):
    rows = []
    for it in items:
        rows.append(
            {
                "paperId": it.get("paperId"),
                "title": it.get("title"),
                "year": it.get("year"),
                "publicationDate": it.get("publicationDate"),
                "citationCount": it.get("citationCount"),
                "publicationTypes": ",".join(it.get("publicationTypes", []) if it.get("publicationTypes") else []),
                "url": it.get("url"),
                "openAccessPdf": it.get("openAccessPdf", {}).get("url") if isinstance(it.get("openAccessPdf"), dict) else None,
            }
        )
    return pd.DataFrame(rows).dropna(subset=["paperId"]).drop_duplicates(subset=["paperId"])


def fetch_details(client, paper_ids, fields):
    """Trae detalles individuales (title, abstract, authors, venue, fields, refs)."""
    import time
    details = []
    errors = []
    (RAW / "details").mkdir(parents=True, exist_ok=True)
    
    print(f"📥 Descargando detalles de {len(paper_ids)} papers...")
    
    for pid in tqdm(paper_ids, desc="Fetching paper details"):
        r = client.get_paper_details(pid, fields)
        if r.status_code == 200 and isinstance(r.data, dict):
            details.append(r.data)
            save_json(r.data, RAW / "details" / f"{pid}.json")
        elif r.status_code == 429:  # Rate limit
            print(f"⚠️ Rate limit en {pid}, esperando...")
            time.sleep(2)
        else:
            errors.append((pid, r.status_code, r.error))
            if len(errors) <= 5:  # Mostrar solo los primeros 5 errores
                print(f"⚠️ Error en {pid}: status={r.status_code}, error={r.error}")
        time.sleep(0.1)  # Pequeño delay para evitar rate limits
    
    if errors:
        print(f"⚠️ Total de errores: {len(errors)} de {len(paper_ids)}")
    print(f"✅ Detalles obtenidos: {len(details)} de {len(paper_ids)}")
    return details


def to_nodes_edges(details):
    """Convierte lista de detalles en dataframes de nodos y aristas."""
    papers, authors, venues, fields = [], [], [], []
    e_authored, e_published, e_topic, e_cites = [], [], [], []
    for d in details:
        pid = d.get("paperId")
        papers.append(
            {
                "paperId": pid,
                "title": d.get("title"),
                "abstract": d.get("abstract"),
                "year": d.get("year"),
                "citationCount": d.get("citationCount"),
                "influentialCitationCount": d.get("influentialCitationCount"),
                "doi": (d.get("externalIds") or {}).get("DOI") if isinstance(d.get("externalIds"), dict) else None,
                "url": d.get("url"),
                "publicationTypes": ",".join(d.get("publicationTypes") or []),
                "venue": d.get("venue"),  # venue viene como string, no como objeto
            }
        )
        # Authors
        for a in d.get("authors", []):
            aid = a.get("authorId")
            if not aid:
                continue
            authors.append({"authorId": aid, "name": a.get("name"), "url": a.get("url")})
            e_authored.append({"paperId": pid, "authorId": aid})
        # Venue (string)
        vname = d.get("venue")  # ahora viene como string
        if vname:
            venues.append({"venueId": vname, "name": vname})  # sin url/type por ahora
            e_published.append({"paperId": pid, "venueId": vname})
        # Fields
        for f in d.get("fieldsOfStudy") or []:
            fields.append({"fieldName": f})
            e_topic.append({"paperId": pid, "fieldName": f})
        # CITES (sin self-edges)
        for ref in d.get("references") or []:
            rid = ref.get("paperId")
            if rid and rid != pid:  # Evitar self-citations
                e_cites.append({"sourcePaperId": pid, "targetPaperId": rid})

    def dd(df, subset):
        return df.drop_duplicates(subset=subset).reset_index(drop=True) if not df.empty else df

    dfs = {
        "papers": dd(pd.DataFrame(papers), ["paperId"]),
        "authors": dd(pd.DataFrame(authors), ["authorId"]),
        "venues": dd(pd.DataFrame(venues), ["venueId"]),
        "fields": dd(pd.DataFrame(fields), ["fieldName"]),
        "paper_authoredby_author": dd(pd.DataFrame(e_authored), ["paperId", "authorId"]),
        "paper_publishedin_venue": dd(pd.DataFrame(e_published), ["paperId", "venueId"]),
        "paper_has_topic": dd(pd.DataFrame(e_topic), ["paperId", "fieldName"]),
        "paper_cites_paper": dd(pd.DataFrame(e_cites), ["sourcePaperId", "targetPaperId"]),
    }
    return dfs


def save_processed(dfs):
    for name, df in dfs.items():
        df.to_csv(PROC / f"{name}.csv", index=False, encoding='utf-8')


def build_summaries(dfs):
    summaries = {}
    papers = dfs["papers"]
    if not papers.empty:
        summaries["summary_year_counts"] = papers.groupby("year", dropna=True).size().reset_index(name="count")
        s_v = dfs["paper_publishedin_venue"].merge(dfs["venues"], on="venueId", how="left")
        summaries["summary_top_venues"] = (
            s_v.groupby(["venueId", "name"], dropna=True)
            .size()
            .reset_index(name="papers")
            .sort_values("papers", ascending=False)
            .head(20)
        )
        s_a = dfs["paper_authoredby_author"].merge(dfs["authors"], on="authorId", how="left")
        summaries["summary_top_authors"] = (
            s_a.groupby(["authorId", "name"], dropna=True)
            .size()
            .reset_index(name="papers")
            .sort_values("papers", ascending=False)
            .head(20)
        )
    for k, v in summaries.items():
        v.to_csv(PROC / f"{k}.csv", index=False, encoding='utf-8')
    return summaries

