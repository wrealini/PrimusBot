import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file googleSheetsToken.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets.readonly"]

BLANK_CSHEET_URL = "https://docs.google.com/spreadsheets/d/1ze4m1sBRoa9giCweh2onYUpWI2jQz3AHZo1rzPAzqWo/edit?usp=sharing"
BLANK_CSHEET_ID = "1ze4m1sBRoa9giCweh2onYUpWI2jQz3AHZo1rzPAzqWo"
CSHEET_URL_HEADER = "https://docs.google.com/spreadsheets/d/"
CSHEET_NAME_RANGE = "v2.1!C6"


creds = None
  # The file googleSheetsToken.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
if os.path.exists("googleSheetsToken.json"):
    creds = Credentials.from_authorized_user_file("googleSheetsToken.json", SCOPES)
# If there are no (valid) credentials available, let the user log in.
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json", SCOPES
        )
        creds = flow.run_local_server(port=0)
    # Save the credentials for the next run
    with open("googleSheetsToken.json", "w") as token:
        token.write(creds.to_json())

class playerCharacter:
  def __init__(self,url):
    self.url = url
    
    if not self.url.startswith(CSHEET_URL_HEADER):
        return
    self.spreadsheet_id = self.url.replace(CSHEET_URL_HEADER,"")
    self.spreadsheet_id = self.spreadsheet_id.partition("/")[0]

    try:
        service = build("sheets", "v4", credentials=creds)

        # Call the Sheets API
        sheet = service.spreadsheets()
        result = (
            sheet.values()
            .get(spreadsheetId=self.spreadsheet_id, range=CSHEET_NAME_RANGE)
            .execute()
        )
        values = result.get("values", [])

        if not values:
            print("No data found.")
            return

        print("Name, Major:")
        for row in values:
        # Print columns A and E, which correspond to indices 0 and 4.
            print(f"{row[0]}")
    except HttpError as err:
        print(err)

pc1 = playerCharacter(BLANK_CSHEET_URL)