def aggregate_by_booth(rows: list, countries: list, top_n: int, exclude_ids: set = None) -> dict:
    """
    rows: list of [type, country, rank, id, use_count, user_count, ...]
    Returns: {country: [(boothId, use_count, user_count), ...]} use_count 내림차순 TOP N
    """
    exclude = exclude_ids or set()
    result = {c: [] for c in countries}
    for row in rows:
        if row[0] != 'boothId':
            continue
        country = row[1]
        if country not in result:
            continue
        item_id = str(row[3])
        if item_id in exclude:
            continue
        result[country].append((item_id, int(row[4] or 0), int(row[5] or 0)))
    for c in countries:
        result[c].sort(key=lambda x: x[1], reverse=True)
        result[c] = result[c][:top_n]
    return result


def aggregate_global(rows: list, id_type: str, top_n: int, exclude_ids: set = None) -> list:
    """
    모든 국가 기준으로 id_type('boothId'|'templateId') 합산.
    Returns: [(id, total_use_count, total_user_count), ...] use_count 내림차순 TOP N
    """
    exclude = exclude_ids or set()
    totals: dict = {}
    for row in rows:
        if row[0] != id_type:
            continue
        item_id = str(row[3])
        if item_id in exclude:
            continue
        if item_id not in totals:
            totals[item_id] = [0, 0]
        totals[item_id][0] += int(row[4] or 0)
        totals[item_id][1] += int(row[5] or 0)
    return sorted(
        [(k, v[0], v[1]) for k, v in totals.items()],
        key=lambda x: -x[1],
    )[:top_n]


def aggregate_by_template(rows: list, countries: list, top_n: int) -> dict:
    """
    rows: list of [type, country, rank, id, use_count, user_count, ...]
    Returns: {country: [(templateId, use_count, user_count), ...]} use_count 내림차순 TOP N
    """
    result = {c: [] for c in countries}
    for row in rows:
        if row[0] != 'templateId':
            continue
        country = row[1]
        if country not in result:
            continue
        result[country].append((str(row[3]), int(row[4] or 0), int(row[5] or 0)))
    for c in countries:
        result[c].sort(key=lambda x: x[1], reverse=True)
        result[c] = result[c][:top_n]
    return result
