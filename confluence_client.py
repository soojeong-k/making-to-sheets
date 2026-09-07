from typing import Optional

import requests

from insight_generator import _th, _td, _table, _thumb_cell

HEADERS = {"Accept": "application/json"}


def _auth_headers(token: str) -> dict:
    return {**HEADERS, "Authorization": f"Bearer {token}"}


def get_page(base_url: str, page_id: str, token: str) -> dict:
    resp = requests.get(
        f"{base_url}/rest/api/content/{page_id}",
        params={"expand": "body.storage,version,title,space"},
        headers=_auth_headers(token),
    )
    resp.raise_for_status()
    return resp.json()


def get_child_page_by_title(base_url: str, parent_page_id: str, token: str, title: str) -> Optional[dict]:
    resp = requests.get(
        f"{base_url}/rest/api/content/search",
        params={
            "cql": f'type=page AND title="{title}" AND ancestor={parent_page_id}',
            "expand": "body.storage,version,title",
        },
        headers=_auth_headers(token),
    )
    resp.raise_for_status()
    results = resp.json().get("results", [])
    return results[0] if results else None


def _create_page(base_url: str, parent_page_id: str, token: str, title: str, body: str, space_key: str) -> dict:
    payload = {
        "type": "page",
        "title": title,
        "ancestors": [{"id": parent_page_id}],
        "space": {"key": space_key},
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    resp = requests.post(
        f"{base_url}/rest/api/content",
        json=payload,
        headers={**_auth_headers(token), "Content-Type": "application/json"},
    )
    resp.raise_for_status()
    return resp.json()


def _update_page_body(base_url: str, page_id: str, token: str, page_data: dict, body: str) -> None:
    payload = {
        "version": {"number": page_data["version"]["number"] + 1},
        "title": page_data["title"],
        "type": "page",
        "body": {"storage": {"value": body, "representation": "storage"}},
    }
    resp = requests.put(
        f"{base_url}/rest/api/content/{page_id}",
        json=payload,
        headers={**_auth_headers(token), "Content-Type": "application/json"},
    )
    resp.raise_for_status()


def _get_children(base_url: str, parent_page_id: str, token: str) -> list:
    resp = requests.get(
        f"{base_url}/rest/api/content/{parent_page_id}/child/page",
        params={"limit": 200, "expand": "version,title"},
        headers=_auth_headers(token),
    )
    resp.raise_for_status()
    return resp.json().get("results", [])


def ensure_child_page(base_url: str, parent_page_id: str, token: str, title: str) -> str:
    for child in _get_children(base_url, parent_page_id, token):
        if child["title"] == title:
            return child["id"]
    parent = get_page(base_url, parent_page_id, token)
    space_key = parent["space"]["key"]
    result = _create_page(base_url, parent_page_id, token, title, "", space_key)
    return result["id"]


def set_page_body(base_url: str, page_id: str, token: str, body: str) -> None:
    page = get_page(base_url, page_id, token)
    _update_page_body(base_url, page_id, token, page, body)



def _country_table_html(country: str, items: list, id_col: str, show_thumbnail: bool = False) -> str:
    num_cols = 5 if show_thumbnail else 4
    country_header = (
        f'<tr><td colspan="{num_cols}" style="background:#333333;color:#ffffff;'
        f'text-align:center;font-weight:bold;padding:6px 10px;border:1px solid #ddd;">'
        f'{country}</td></tr>'
    )
    if show_thumbnail:
        col_headers = _th("No") + _th(id_col) + _th("thumbnail") + _th("use_count") + _th("user_count")
    else:
        col_headers = _th("No") + _th(id_col) + _th("use_count") + _th("user_count")

    link_prefix = "https://web.zepeto.me/share/template/" if id_col == "templateId" else None

    rows = []
    for i, (item_id, use_count, user_count) in enumerate(items):
        if link_prefix:
            id_cell = f'<code>{item_id}</code> <a href="{link_prefix}{item_id}">[링크]</a>'
        else:
            id_cell = f'<code>{item_id}</code>'
        row = _td(str(i + 1)) + _td(id_cell, align="left")
        if show_thumbnail:
            row += _thumb_cell(item_id)
        row += _td(f"{use_count:,}") + _td(f"{user_count:,}")
        rows.append(f"<tr>{row}</tr>")

    rows_html = "".join(rows)
    table = (
        '<table style="border-collapse:collapse;width:auto;margin:0;">'
        f'<thead>{country_header}<tr>{col_headers}</tr></thead>'
        f'<tbody>{rows_html}</tbody>'
        '</table>'
    )
    return f'<div style="display:inline-block;vertical-align:top;margin-right:16px;">{table}</div>'


def _ranking_horizontal_html(grouped: dict, id_col: str, title: str, countries: list, top_k: int = 100, show_thumbnail: bool = False) -> str:
    blocks = "".join(
        _country_table_html(c, grouped.get(c, [])[:top_k], id_col, show_thumbnail)
        for c in countries
    )
    return (
        f"<h3>{title}</h3>"
        f'<div style="white-space:nowrap;overflow-x:auto;">{blocks}</div>'
    )


def build_making_body(
    booth_grouped: dict,
    template_grouped: dict,
    countries: list,
    insights_html: str,
) -> str:
    booth_table = _ranking_horizontal_html(booth_grouped, "boothId", "부스 랭킹 TOP100", countries, top_k=100, show_thumbnail=True)
    template_table = _ranking_horizontal_html(template_grouped, "templateId", "템플릿 랭킹 TOP100", countries, top_k=100)
    return insights_html + "<hr />" + booth_table + "<br />" + template_table
