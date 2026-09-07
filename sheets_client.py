import os
import pickle
import time

import gspread
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow

SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_PATH = os.path.join(os.path.dirname(__file__), "token.pickle")


def get_spreadsheet(sheet_id: str, credentials_path: str):
    creds = None
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as f:
            creds = pickle.load(f)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)
        with open(TOKEN_PATH, "wb") as f:
            pickle.dump(creds, f)
    client = gspread.authorize(creds)
    return client.open_by_key(sheet_id)


def create_worksheet(spreadsheet, title: str):
    return spreadsheet.add_worksheet(title=title, rows=200, cols=30)


def _col_letter(n: int) -> str:
    result = ""
    while n > 0:
        n, remainder = divmod(n - 1, 26)
        result = chr(65 + remainder) + result
    return result


def _build_data_batch(rows: list) -> list:
    """rows: [(id, use_count, user_count), ...] → [[rank, id, use_count, user_count], ...]"""
    return [[i + 1, row[0], row[1], row[2]] for i, row in enumerate(rows)]


def _write_country_block(ws, country: str, rows: list, id_col_name: str, col_offset: int, include_thumbnail: bool = False) -> None:
    """col_offset: 1-based. Columns: No | id | [thumbnail] | use_count | user_count."""
    num_cols = 5 if include_thumbnail else 4
    start = _col_letter(col_offset)
    end = _col_letter(col_offset + num_cols - 1)
    id_col = _col_letter(col_offset + 1)
    if include_thumbnail:
        use_col = _col_letter(col_offset + 3)
        user_col = _col_letter(col_offset + 4)
        headers = [["No", id_col_name, "thumbnail", "use_count", "user_count"]]
    else:
        use_col = _col_letter(col_offset + 2)
        user_col = _col_letter(col_offset + 3)
        headers = [["No", id_col_name, "use_count", "user_count"]]

    ws.update(f"{start}1", [[country]])
    time.sleep(1)
    ws.format(f"{start}1:{end}1", {
        "backgroundColor": {"red": 0.2, "green": 0.2, "blue": 0.2},
        "textFormat": {
            "foregroundColor": {"red": 1.0, "green": 1.0, "blue": 1.0},
            "bold": True,
        },
        "horizontalAlignment": "CENTER",
    })
    time.sleep(1)
    ws.merge_cells(f"{start}1:{end}1")
    time.sleep(1)
    ws.update(f"{start}2:{end}2", headers)
    time.sleep(1)
    ws.format(f"{start}2:{end}2", {"textFormat": {"bold": True}})
    time.sleep(1)

    if rows:
        if include_thumbnail:
            batch = []
            for i, row in enumerate(rows):
                sheet_row = 3 + i
                formula = f'=IMAGE("http://cdn-asset.zepeto.me/assets/"&{id_col}{sheet_row}&"/thumbnail",1)'
                batch.append([i + 1, row[0], formula, row[1], row[2]])
        else:
            batch = _build_data_batch(rows)
        ws.update(
            f"{start}3:{end}{2 + len(rows)}",
            batch,
            value_input_option="USER_ENTERED",
        )
        time.sleep(1)
        ws.format(f"{use_col}3:{user_col}{2 + len(rows)}", {
            "numberFormat": {"type": "NUMBER", "pattern": "#,##0"}
        })
        time.sleep(1)


def write_making_tab(ws, grouped: dict, id_col_name: str, include_thumbnail: bool = False) -> None:
    """
    grouped: {country: [(id, use_count, user_count), ...]}
    id_col_name: 'boothId' or 'templateId'
    """
    col_offset = 1
    block_width = 6 if include_thumbnail else 5  # data cols + 1 separator col
    for country, rows in grouped.items():
        _write_country_block(ws, country, rows, id_col_name, col_offset, include_thumbnail)
        col_offset += block_width
        time.sleep(3)


def format_worksheet_dimensions(ws, spreadsheet, num_countries: int, include_thumbnail: bool = False) -> None:
    sheet_id = ws.id
    if include_thumbnail:
        col_widths = [38, 220, 80, 90, 90]  # No, ID, thumbnail, use_count, user_count
        block_width = 6
        data_row_height = 60
    else:
        col_widths = [38, 220, 90, 90]  # No, ID, use_count, user_count
        block_width = 5
        data_row_height = 22
    separator_width = 18

    reqs = []
    for i in range(num_countries):
        base = i * block_width
        for j, width in enumerate(col_widths):
            reqs.append({"updateDimensionProperties": {
                "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                          "startIndex": base + j, "endIndex": base + j + 1},
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }})
        reqs.append({"updateDimensionProperties": {
            "range": {"sheetId": sheet_id, "dimension": "COLUMNS",
                      "startIndex": base + len(col_widths), "endIndex": base + len(col_widths) + 1},
            "properties": {"pixelSize": separator_width},
            "fields": "pixelSize",
        }})

    reqs.append({"updateDimensionProperties": {
        "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": 0, "endIndex": 2},
        "properties": {"pixelSize": 26},
        "fields": "pixelSize",
    }})
    reqs.append({"updateDimensionProperties": {
        "range": {"sheetId": sheet_id, "dimension": "ROWS", "startIndex": 2, "endIndex": 102},
        "properties": {"pixelSize": data_row_height},
        "fields": "pixelSize",
    }})

    spreadsheet.batch_update({"requests": reqs})
