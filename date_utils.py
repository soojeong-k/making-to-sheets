from calendar import monthrange


def get_previous_month_range(year: int, month: int) -> tuple:
    if month == 1:
        prev_year, prev_month = year - 1, 12
    else:
        prev_year, prev_month = year, month - 1
    _, last_day = monthrange(prev_year, prev_month)
    start = f"{prev_year}-{prev_month:02d}-01"
    end = f"{prev_year}-{prev_month:02d}-{last_day:02d}"
    return start, end


def get_sheet_tab_prefix(year: int, month: int) -> str:
    if month == 1:
        return f"{year - 1}12"
    return f"{year}{month - 1:02d}"


def get_confluence_title(year: int, month: int) -> str:
    if month == 1:
        return f"{year - 1}.12"
    return f"{year}.{month - 1:02d}"
