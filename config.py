import os
from dotenv import load_dotenv

load_dotenv()

ZETTA_API_KEY = os.environ["ZETTA_API_KEY"]
MAKING_INSIGHT_SHORT_ID = "QGS5Jdtp"
COUNTRIES = ["US", "KR", "JP", "ID", "FR"]

GOOGLE_SHEET_ID = os.environ["GOOGLE_SHEET_ID"]
GOOGLE_CREDENTIALS_PATH = os.environ.get("GOOGLE_CREDENTIALS_PATH", "./oauth_client.json")

CONFLUENCE_BASE_URL = os.environ.get("CONFLUENCE_BASE_URL", "https://wiki.navercorp.com")
CONFLUENCE_TOKEN = os.environ.get("CONFLUENCE_TOKEN", "")
CONFLUENCE_PAGE_ID = os.environ.get("CONFLUENCE_PAGE_ID", "5262047746")

RANKING_TOP_N = 100
BOOTH_EXCLUDE_IDS = {"VIDEOBOOTH_ANI_62"}
