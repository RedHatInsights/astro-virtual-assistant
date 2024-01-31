from csv import reader
from os import getenv
from typing import Text, List

import gspread
from google.oauth2.service_account import Credentials


def fetch_csv(csv_file: Text) -> List:
    with open(csv_file) as input:
        return list(reader(input))


def dump_to_google_sheet(
    spreadsheet_id: Text, worksheet_name: Text, data: List, credentials: Credentials
):
    client = gspread.authorize(credentials)
    spreadsheet = client.open_by_key(spreadsheet_id)
    ws = spreadsheet.worksheet(worksheet_name)
    ws.clear()
    ws.update(data, "A1")


if __name__ == "__main__":
    spreadsheet_id = getenv("SPREADSHEET_ID")
    worksheet_name = getenv("WORKSHEET_NAME")

    service_account_info = {
        "token_uri": "https://oauth2.googleapis.com/token",
        "client_email": getenv("GOOGLE_CLOUD_ACCOUNT"),
        "private_key": getenv("GOOGLE_CLOUD_ACCOUNT_SECRET").replace("\\n", "\n"),
    }
    scopes = [
        "https://spreadsheets.google.com/feeds",
    ]

    credentials = Credentials.from_service_account_info(
        service_account_info, scopes=scopes
    )

    data = fetch_csv("./intents.csv")
    dump_to_google_sheet(spreadsheet_id, worksheet_name, data, credentials)
