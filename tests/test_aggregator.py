from aggregator import aggregate_by_booth, aggregate_by_template

# rows: [type, country, rank, id, use_count, user_count, extra]
ROWS = [
    ['boothId', 'US', 1, 'booth1', 300, 130, 1],
    ['boothId', 'US', 2, 'booth2', 150, 60, 2],
    ['boothId', 'KR', 1, 'booth3', 400, 200, 1],
    ['boothId', 'KR', 2, 'booth1', 50, 30, 2],
    ['templateId', 'US', 1, 'tmpl1', 250, 110, 1],
    ['templateId', 'US', 2, 'tmpl2', 100, 40, 2],
    ['templateId', 'KR', 1, 'tmpl3', 300, 150, 1],
    ['boothId', 'XX', 1, 'booth9', 999, 999, 1],  # 대상 외 국가 → 무시
]


def test_aggregate_by_booth_returns_booth_rows_only():
    result = aggregate_by_booth(ROWS, ['US', 'KR'], top_n=100)
    ids = [r[0] for r in result['US']]
    assert 'booth1' in ids
    assert 'tmpl1' not in ids


def test_aggregate_by_booth_sorted_desc():
    result = aggregate_by_booth(ROWS, ['US'], top_n=100)
    use_counts = [r[1] for r in result['US']]
    assert use_counts == sorted(use_counts, reverse=True)


def test_aggregate_by_booth_respects_top_n():
    result = aggregate_by_booth(ROWS, ['US'], top_n=1)
    assert len(result['US']) == 1
    assert result['US'][0][1] == 300  # booth1이 TOP1


def test_aggregate_by_booth_ignores_unknown_country():
    result = aggregate_by_booth(ROWS, ['JP'], top_n=100)
    assert result['JP'] == []


def test_aggregate_by_template_returns_template_rows_only():
    result = aggregate_by_template(ROWS, ['US', 'KR'], top_n=100)
    ids = [r[0] for r in result['US']]
    assert 'tmpl1' in ids
    assert 'booth1' not in ids


def test_aggregate_by_template_sorted_desc():
    result = aggregate_by_template(ROWS, ['US'], top_n=100)
    use_counts = [r[1] for r in result['US']]
    assert use_counts == sorted(use_counts, reverse=True)


def test_aggregate_by_template_ignores_unknown_country():
    result = aggregate_by_template(ROWS, ['JP'], top_n=100)
    assert result['JP'] == []
