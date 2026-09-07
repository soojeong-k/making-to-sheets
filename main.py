from datetime import date

import config
from aggregator import aggregate_by_booth, aggregate_by_template, aggregate_global
from confluence_client import build_making_body, ensure_child_page, set_page_body
from date_utils import get_confluence_title, get_previous_month_range, get_sheet_tab_prefix
from insight_generator import generate_insights
from sheets_client import (
    create_worksheet,
    format_worksheet_dimensions,
    get_spreadsheet,
    write_making_tab,
)
from zetta_client import build_global_query, fetch_insight_query, fetch_making_data, replace_date_range


def run():
    today = date.today()
    start, end = get_previous_month_range(today.year, today.month)
    tab_prefix = get_sheet_tab_prefix(today.year, today.month)
    confluence_title = get_confluence_title(today.year, today.month)

    booth_tab = f"{tab_prefix}_부스랭킹_국가별"
    template_tab = f"{tab_prefix}_템플릿랭킹_국가별"
    # Prefix to avoid Confluence space-wide title collision with other pipelines (e.g. zetta-to-sheets)
    confluence_child_title = f"[만들기] {confluence_title}"

    print(f"[making-to-sheets] 조회 기간: {start} ~ {end}")

    # Zetta 데이터 조회
    query = fetch_insight_query(config.MAKING_INSIGHT_SHORT_ID, api_key=config.ZETTA_API_KEY)
    query = replace_date_range(query, start, end)
    rows = fetch_making_data(query, api_key=config.ZETTA_API_KEY)
    print(f"[making-to-sheets] 총 {len(rows)}개 행 조회")

    # 집계
    booth_grouped = aggregate_by_booth(rows, config.COUNTRIES, config.RANKING_TOP_N, exclude_ids=config.BOOTH_EXCLUDE_IDS)
    template_grouped = aggregate_by_template(rows, config.COUNTRIES, config.RANKING_TOP_N)

    # 전체 국가 기준 집계 (국가 필터 제거 후 별도 조회)
    global_rows = fetch_making_data(build_global_query(query), api_key=config.ZETTA_API_KEY)
    print(f"[making-to-sheets] 전체 국가 {len(global_rows)}개 행 조회")
    booth_global = aggregate_global(global_rows, 'boothId', config.RANKING_TOP_N, exclude_ids=config.BOOTH_EXCLUDE_IDS)
    template_global = aggregate_global(global_rows, 'templateId', config.RANKING_TOP_N)

    # Google Sheets
    spreadsheet = get_spreadsheet(config.GOOGLE_SHEET_ID, config.GOOGLE_CREDENTIALS_PATH)
    existing_tabs = [ws.title for ws in spreadsheet.worksheets()]

    if booth_tab not in existing_tabs:
        ws = create_worksheet(spreadsheet, booth_tab)
        write_making_tab(ws, booth_grouped, "boothId", include_thumbnail=True)
        format_worksheet_dimensions(ws, spreadsheet, num_countries=len(config.COUNTRIES), include_thumbnail=True)
        print(f"[making-to-sheets] '{booth_tab}' 탭 생성 완료")
    else:
        print(f"[making-to-sheets] '{booth_tab}' 이미 존재, 스킵")

    if template_tab not in existing_tabs:
        ws = create_worksheet(spreadsheet, template_tab)
        write_making_tab(ws, template_grouped, "templateId")
        format_worksheet_dimensions(ws, spreadsheet, num_countries=len(config.COUNTRIES))
        print(f"[making-to-sheets] '{template_tab}' 탭 생성 완료")
    else:
        print(f"[making-to-sheets] '{template_tab}' 이미 존재, 스킵")

    # Confluence
    print(f"[making-to-sheets] Confluence '{confluence_child_title}' 페이지 업데이트 중...")
    child_page_id = ensure_child_page(
        config.CONFLUENCE_BASE_URL,
        config.CONFLUENCE_PAGE_ID,
        config.CONFLUENCE_TOKEN,
        confluence_child_title,
    )
    insights_html = generate_insights(booth_grouped, template_grouped, config.COUNTRIES, booth_global, template_global)
    body = build_making_body(booth_grouped, template_grouped, config.COUNTRIES, insights_html)
    set_page_body(config.CONFLUENCE_BASE_URL, child_page_id, config.CONFLUENCE_TOKEN, body)
    print(f"[making-to-sheets] 완료: Confluence '{confluence_child_title}'")


if __name__ == "__main__":
    run()
