from insight_generator import (
    generate_insights,
    _usage_summary_section,
    _cross_country_section,
    _per_user_section,
)

BOOTH = {
    "US": [("booth1", 5000, 2000), ("booth2", 3000, 1500)],
    "KR": [("booth3", 4000, 1800), ("booth1", 2000, 900)],
    "JP": [],
    "ID": [],
    "FR": [],
}

TEMPLATE = {
    "US": [("tmpl1", 6000, 2500), ("tmpl2", 1000, 400)],
    "KR": [("tmpl2", 3500, 1200)],
    "JP": [],
    "ID": [],
    "FR": [],
}

COUNTRIES = ["US", "KR", "JP", "ID", "FR"]


def test_generate_insights_returns_html_with_tables():
    html = generate_insights(BOOTH, TEMPLATE, COUNTRIES)
    assert "<table" in html
    assert "<h3>" in html


def test_usage_summary_contains_top1_ids():
    html = _usage_summary_section(BOOTH, TEMPLATE, COUNTRIES)
    assert "booth1" in html   # US TOP1
    assert "tmpl1" in html    # US template TOP1


def test_cross_country_detects_common_item():
    html = _cross_country_section(BOOTH, COUNTRIES, "부스")
    assert "booth1" in html   # booth1은 US와 KR 모두 TOP20 진입


def test_cross_country_no_common_returns_message():
    isolated = {
        "US": [("onlyUS", 100, 50)],
        "KR": [("onlyKR", 100, 50)],
        "JP": [], "ID": [], "FR": [],
    }
    html = _cross_country_section(isolated, COUNTRIES, "부스")
    assert "없음" in html


def test_per_user_section_calculates_ratio():
    html = _per_user_section(BOOTH, COUNTRIES)
    # US: total use=8000, total user=3500 → ratio=2.29
    assert "2.29" in html or "2.28" in html  # float rounding
