import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file googleSheetsToken.json.
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]

BLANK_CSHEET_URL = "https://docs.google.com/spreadsheets/d/1ze4m1sBRoa9giCweh2onYUpWI2jQz3AHZo1rzPAzqWo/edit?usp=sharing"
BLANK_CSHEET_ID = "1ze4m1sBRoa9giCweh2onYUpWI2jQz3AHZo1rzPAzqWo"
CSHEET_URL_HEADER = "https://docs.google.com/spreadsheets/d/"
CSHEET_RANGE = ["name","level","classAndLevel","race","experience",
                "strAP","strAPBonus","strScore","strMod","dexAP","dexAPBonus","dexScore","dexMod",
                "conAP","conAPBonus","conScore","conMod","intAP","intAPBonus","intScore","intMod",
                "wisAP","wisAPBonus","wisScore","wisMod","chaAP","chaAPBonus","chaScore","chaMod"]

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

import sqlite3
from sqlite3 import Error

try:
    connection = sqlite3.connect("playerCharacters.db")
    print("Connection to SQLite DB successful")
except Error as e:
    print(f"The error '{e}' occurred")
cursor = connection.cursor()
command = '''Create TABLE if not exists playerCharacters('''
for csrange in CSHEET_RANGE:
    command = command+csrange+''' TEXT, '''
command = command+'''csheet_url TEXT, csheet_id TEXT PRIMARY KEY)'''
cursor.execute(command)

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
            values = sheet.values()
            result = values.batchGet(spreadsheetId=self.spreadsheet_id, ranges=CSHEET_RANGE).execute().get("valueRanges", [])

            if not result:
                print("No data found.")
                return

            self.data = dict()
            for i in range(len(CSHEET_RANGE)):
                self.data.update({CSHEET_RANGE[i]: result[i].get("values", [[""]])[0][0]})

            print("Character Sheet gsheet loading successful")
            print("URL: "+self.url)
            print("SPREADSHEET_ID: "+self.spreadsheet_id)
            # for i in range(len(CSHEET_RANGE)):
            #     print(CSHEET_RANGE[i]+": "+str(self.data.get(CSHEET_RANGE[i])))
        except HttpError as err:
            print(err)

    def updateDatabase(self):
        try:
            cdata = dict(self.data)
            cdata.update({"csheet_url":self.url,"csheet_id":self.spreadsheet_id})
            cdata = tuple(cdata.values())
            command = "INSERT INTO playerCharacters VALUES("+("?,"*len(CSHEET_RANGE))+"?,?)"
            cursor.execute(command,cdata)
            connection.commit()
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
            try:
                command = "UPDATE playerCharacters SET "
                for csrange in CSHEET_RANGE:
                    command = command+csrange+" = ?, "
                command = command+"csheet_url = ? WHERE csheet_id = ?"
                cursor.execute(command,cdata)
                connection.commit()
            except sqlite3.Error as e:
                print(f"The error '{e}' occurred")

    def readDatabase(self,csheet_id):
        try:
            cursor.execute("SELECT * FROM playerCharacters WHERE csheet_id = ?",(csheet_id,))
            rows = cursor.fetchall()
        except sqlite3.Error as e:
            print(f"The error '{e}' occurred")
        if not rows:
            return False
        if len(rows[0]) != len(CSHEET_RANGE)+2:
            return False
        cdata = dict()
        for i in range(len(CSHEET_RANGE)):
            cdata.update({CSHEET_RANGE[i]: rows[0][i]})
        self.data = cdata
        self.url = rows[0][len(CSHEET_RANGE)]
        self.spreadsheet_id = rows[0][len(CSHEET_RANGE)+1]
        return True


pc1 = playerCharacter(BLANK_CSHEET_URL)
pc1.updateDatabase()
pc1.readDatabase(BLANK_CSHEET_ID)
cursor.execute("SELECT * FROM playerCharacters")
rows = cursor.fetchall()
for row in rows:
    print(row)

connection.close()