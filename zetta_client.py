import re
import requests


def fetch_insight_query(short_id: str, api_key: str) -> str:
    url = "https://zepeto.zetta.so/api/projects/1/insights/"
    params = {
        "short_id": short_id,
        "include_query_insights": "true",
        "cached": "true",
    }
    headers = {"Authorization": f"Bearer {api_key}"}
    response = requests.get(url, params=params, headers=headers, timeout=60)
    response.raise_for_status()
    data = response.json()
    if not data.get("results"):
        raise ValueError(f"Insight not found: {short_id}")
    return data["results"][0]["query"]["source"]["query"]


def replace_date_range(query: str, start: str, end: str) -> str:
    # Pattern used by making insight: CTE constants toDate('YYYY-MM-DD') AS DATE_FROM / DATE_TO
    date_from_pattern = r"toDate\('[^']+'\)\s*AS\s*DATE_FROM"
    date_to_pattern = r"toDate\('[^']+'\)\s*AS\s*DATE_TO"
    if re.search(date_from_pattern, query) and re.search(date_to_pattern, query):
        query = re.sub(date_from_pattern, f"toDate('{start}') AS DATE_FROM", query)
        query = re.sub(date_to_pattern, f"toDate('{end}') AS DATE_TO", query)
        return query

    # Fallback: pattern used by zetta-to-sheets insight (timestamp >= toDateTime(...))
    gte_pattern = r"timestamp\s*>=\s*toDateTime\('[^']+',\s*'Asia/Seoul'\)"
    lt_pattern = r"timestamp\s*<\s*toDateTime\('[^']+',\s*'Asia/Seoul'\)"
    if re.search(gte_pattern, query) and re.search(lt_pattern, query):
        query = re.sub(gte_pattern, f"timestamp >= toDateTime('{start}', 'Asia/Seoul')", query)
        query = re.sub(lt_pattern, f"timestamp < toDateTime('{end}', 'Asia/Seoul')", query)
        return query

    raise ValueError("Could not find timestamp conditions in query")


def execute_hogql(query: str, api_key: str) -> list:
    url = "https://zepeto.zetta.so/api/projects/1/query"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    body = {"query": {"kind": "HogQLQuery", "query": query}}
    response = requests.post(url, json=body, headers=headers, timeout=180)
    response.raise_for_status()
    return response.json()["results"]


def build_global_query(query: str) -> str:
    """국가 필터(geoip_country_code IN ...)를 제거해 전체 국가 데이터를 조회하는 쿼리로 변환."""
    query = re.sub(
        r"\s*AND properties\.\$geoip_country_code IN \([^)]+\)",
        "",
        query,
    )
    # 전체 국가는 행 수가 많아질 수 있으므로 LIMIT를 충분히 늘림
    query = re.sub(r"\bLIMIT\s+\d+", "LIMIT 50000", query)
    return query


def fetch_making_data(query: str, api_key: str) -> list:
    """전체 국가 데이터를 한 번에 조회. rows: (country, boothId, templateId, use_count, user_count)"""
    return execute_hogql(query, api_key)
