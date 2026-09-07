def _fmt(n: int) -> str:
    return f"{n:,}"


def _tmpl_id_cell(item_id: str) -> str:
    link = f'https://web.zepeto.me/share/template/{item_id}'
    return f'<code>{item_id}</code> <a href="{link}">[링크]</a>'


def _thumb_cell(item_id: str) -> str:
    url = f"http://cdn-asset.zepeto.me/assets/{item_id}/thumbnail"
    img = (
        f'<ac:image ac:alt="{item_id}" ac:width="50">'
        f'<ri:url ri:value="{url}"/>'
        f'</ac:image>'
    )
    return _td(img)


def _th(text: str) -> str:
    return (
        f'<th style="background:#f0f0f0;padding:6px 10px;text-align:center;'
        f'white-space:nowrap;border:1px solid #ddd;">{text}</th>'
    )


def _td(text: str, align: str = "center") -> str:
    return f'<td style="padding:5px 10px;text-align:{align};border:1px solid #ddd;">{text}</td>'


def _table(header_row: str, body_rows: list) -> str:
    rows_html = "".join(f"<tr>{r}</tr>" for r in body_rows)
    return (
        '<table style="border-collapse:collapse;width:auto;margin-bottom:12px;">'
        f"<thead><tr>{header_row}</tr></thead>"
        f"<tbody>{rows_html}</tbody>"
        "</table>"
    )


def _usage_summary_section(booth_grouped: dict, template_grouped: dict, countries: list, booth_global: list, template_global: list) -> str:
    header = (
        _th("국가") +
        _th("부스 TOP1 ID") + _th("부스 썸네일") + _th("부스 TOP1 use_count") +
        _th("템플릿 TOP1 ID") + _th("템플릿 TOP1 use_count")
    )
    rows = []
    for c in countries:
        booth = booth_grouped.get(c, [])
        tmpl = template_grouped.get(c, [])
        b1_id = f'<code>{booth[0][0]}</code>' if booth else "-"
        b1_use = _fmt(booth[0][1]) if booth else "-"
        t1_id = _tmpl_id_cell(tmpl[0][0]) if tmpl else "-"
        t1_use = _fmt(tmpl[0][1]) if tmpl else "-"
        rows.append(
            _td(f"<strong>{c}</strong>") +
            _td(b1_id, align="left") +
            (_thumb_cell(booth[0][0]) if booth else _td("-")) +
            _td(b1_use) +
            _td(t1_id, align="left") + _td(t1_use)
        )

    # 전체 국가 합산 기준 TOP1
    ab_id = f'<code>{booth_global[0][0]}</code>' if booth_global else "-"
    ab_use = _fmt(booth_global[0][1]) if booth_global else "-"
    at_id = _tmpl_id_cell(template_global[0][0]) if template_global else "-"
    at_use = _fmt(template_global[0][1]) if template_global else "-"
    rows.append(
        _td("<strong>전체</strong>") +
        _td(ab_id, align="left") +
        (_thumb_cell(booth_global[0][0]) if booth_global else _td("-")) +
        _td(ab_use) +
        _td(at_id, align="left") + _td(at_use)
    )
    return "<h3>국가별 TOP1 요약</h3>" + _table(header, rows)


def _per_user_section(booth_grouped: dict, countries: list, booth_global: list) -> str:
    header = _th("국가") + _th("총 use_count") + _th("총 user_count") + _th("1인당 평균 사용")
    rows = []
    for c in countries:
        items = booth_grouped.get(c, [])
        if not items:
            rows.append(_td(f"<strong>{c}</strong>") + _td("-") + _td("-") + _td("-"))
            continue
        total_use = sum(r[1] for r in items)
        total_user = sum(r[2] for r in items)
        ratio = total_use / total_user if total_user else 0
        rows.append(
            _td(f"<strong>{c}</strong>") +
            _td(_fmt(total_use)) +
            _td(_fmt(total_user)) +
            _td(f"{ratio:.2f}")
        )

    # 전체 국가 합산
    grand_use = sum(r[1] for r in booth_global)
    grand_user = sum(r[2] for r in booth_global)
    grand_ratio = grand_use / grand_user if grand_user else 0
    rows.append(
        _td("<strong>전체</strong>") +
        _td(_fmt(grand_use)) +
        _td(_fmt(grand_user)) +
        _td(f"{grand_ratio:.2f}")
    )
    return "<h3>1인당 평균 사용 횟수 (부스 기준)</h3>" + _table(header, rows)


def _cross_country_section(grouped: dict, countries: list, label: str, top_k: int = 20, show_thumbnail: bool = False) -> str:
    appearances: dict = {}
    for c in countries:
        for rank, row in enumerate(grouped.get(c, [])[:top_k]):
            item_id = row[0]
            appearances.setdefault(item_id, []).append((c, rank + 1))

    hits = sorted(
        [(k, v) for k, v in appearances.items() if len(v) >= 2],
        key=lambda x: -len(x[1]),
    )
    if not hits:
        return (
            f"<h3>공통 인기 {label} (TOP{top_k} 기준)</h3>"
            f"<p>2개국 이상 TOP{top_k} 동시 진입 항목 없음</p>"
        )

    if show_thumbnail:
        header = _th("ID") + _th("thumbnail") + _th("진입 국가 수") + _th("국가별 순위")
    else:
        header = _th("ID") + _th("진입 국가 수") + _th("국가별 순위")
    is_template = (label == "템플릿")
    rows = []
    for item_id, app_list in hits:
        country_ranks = " · ".join(f"{c} #{r}" for c, r in sorted(app_list, key=lambda x: x[1]))
        id_html = _tmpl_id_cell(item_id) if is_template else f'<code>{item_id}</code>'
        row = _td(id_html, align="left")
        if show_thumbnail:
            row += _thumb_cell(item_id)
        row += _td(str(len(app_list))) + _td(country_ranks, align="left")
        rows.append(row)
    return f"<h3>공통 인기 {label} (TOP{top_k} 기준)</h3>" + _table(header, rows)


def generate_insights(booth_grouped: dict, template_grouped: dict, countries: list, booth_global: list = None, template_global: list = None) -> str:
    booth_global = booth_global or []
    template_global = template_global or []
    return "".join([
        _usage_summary_section(booth_grouped, template_grouped, countries, booth_global, template_global),
        "<br />",
        _per_user_section(booth_grouped, countries, booth_global),
        "<br />",
        _cross_country_section(booth_grouped, countries, "부스", show_thumbnail=True),
        "<br />",
        _cross_country_section(template_grouped, countries, "템플릿"),
    ])
