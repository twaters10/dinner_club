import gspread
import pandas as pd
from oauth2client.service_account import ServiceAccountCredentials
'/Users/tawate/Documents/Dinner Club/clean-terminal-468616-k8-06169f567f7e.json'
"Dinner Club Ranking (Responses)"

def ingest_data(google_sheets_json_path, spreadsheet_title) -> pd.DataFrame:
    # Step 1: Authenticate with Google Sheets
    # Define the scope and path to your service account key file
    scope = ['https://spreadsheets.google.com/feeds',
            'https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name(google_sheets_json_path, scope)
    client = gspread.authorize(creds)

    # Step 2: Open the spreadsheet
    # You can open it by title, key, or URL
    try:
        # Open by title
        sheet = client.open(spreadsheet_title).sheet1  # Use .sheet1 for the first worksheet

        # Or, open by spreadsheet key (the long string in the URL)
        # sheet = client.open_by_key("your-spreadsheet-key").sheet1

        # Or, open by URL
        # sheet_url = "https://docs.google.com/spreadsheets/d/your-spreadsheet-key/edit"
        # sheet = client.open_by_url(sheet_url).sheet1

    except gspread.exceptions.SpreadsheetNotFound:
        print("Spreadsheet not found. Please check the title and sharing permissions.")
        exit()

    # Step 3: Get all the data from the worksheet
    data = sheet.get_all_values()

    # Step 4: Convert the data into a pandas DataFrame
    # The first row is typically the header
    headers = data[0]
    df = pd.DataFrame(data[1:], columns=headers)
    return df