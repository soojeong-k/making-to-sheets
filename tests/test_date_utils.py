from date_utils import get_previous_month_range, get_sheet_tab_prefix, get_confluence_title


def test_previous_month_range_normal():
    start, end = get_previous_month_range(2026, 5)
    assert start == "2026-04-01"
    assert end == "2026-04-30"


def test_previous_month_range_january_crosses_year():
    start, end = get_previous_month_range(2026, 1)
    assert start == "2025-12-01"
    assert end == "2025-12-31"


def test_previous_month_range_march_has_28_days():
    start, end = get_previous_month_range(2026, 3)
    assert start == "2026-02-01"
    assert end == "2026-02-28"


def test_sheet_tab_prefix_normal():
    assert get_sheet_tab_prefix(2026, 5) == "202604"


def test_sheet_tab_prefix_january():
    assert get_sheet_tab_prefix(2026, 1) == "202512"


def test_confluence_title_normal():
    assert get_confluence_title(2026, 5) == "2026.04"


def test_confluence_title_january():
    assert get_confluence_title(2026, 1) == "2025.12"
