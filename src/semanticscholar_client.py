import time
import requests
from dataclasses import dataclass
from .config import settings


@dataclass
class S2Response:
    status_code: int
    data: dict | list | None
    error: str | None = None
    next_token: str | None = None


class SemanticScholarClient:
    """Cliente simple para Academic Graph API (bulk search + paper details)."""

    def __init__(self, api_key: str | None = None):
        self.base = settings.base_url
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "UTPL-PrecisionAgri-KG/0.1"})
        key = api_key or settings.api_key
        if key:
            self.session.headers["x-api-key"] = key

    def _request(self, method, path, params=None):
        url = f"{self.base}/{path.lstrip('/')}"
        for attempt in range(settings.max_retries):
            try:
                r = self.session.request(method, url, params=params, timeout=settings.timeout)
                if r.status_code == 200:
                    data = r.json()
                    token = data.get("token") if isinstance(data, dict) else None
                    return S2Response(200, data, None, token)
                if r.status_code == 429:  # rate limit
                    time.sleep(2 ** attempt)
                    continue
                return S2Response(r.status_code, None, r.text)
            except requests.RequestException as e:
                if attempt == settings.max_retries - 1:
                    return S2Response(0, None, str(e))
                time.sleep(2 ** attempt)
        return S2Response(0, None, "Unknown error")

    # ---- Bulk search (con filtros y token de paginación) ----
    def search_papers_bulk(self, query, fields, year=None, publication_types=None, sort=None, token=None):
        params = {"query": query, "fields": fields}
        if year:
            params["year"] = year
        if publication_types:
            params["publicationTypes"] = publication_types
        if sort:
            params["sort"] = sort
        if token:
            params["token"] = token
        return self._request("GET", "/paper/search/bulk", params)

    # ---- Details ----
    def get_paper_details(self, paper_id, fields):
        return self._request("GET", f"/paper/{paper_id}", {"fields": fields})

    # ---- Author details ----
    def get_author_details(self, author_id, fields="authorId,name,affiliations,url,paperCount,citationCount"):
        return self._request("GET", f"/author/{author_id}", {"fields": fields})

