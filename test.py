import json
import time
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import requests

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/photospicker.mediaitems.readonly"]

# The ID of a sample document.
DOCUMENT_ID = "195j9eDD3ccgjQRttHhJPymLJUCOUjs-jmwTrekvdjFE"


def main():
  """Shows basic usage of the Docs API.
  Prints the title of a sample document.
  """
  creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists("token.json"):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)
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
    with open("token.json", "w") as token:
      token.write(creds.to_json())

  try:
    headers = {
        "Authorization": f"Bearer {creds.token}"
    }
    r = requests.post("https://photospicker.googleapis.com/v1/sessions", headers=headers)

    r_json = r.json()
    print(f"Got session {json.dumps(r_json)}")

    session_id = r_json["id"]
    photos_selected = False
    while not photos_selected:
        polling_interval = int(r_json["pollingConfig"]["pollInterval"][:-1])
        time.sleep(polling_interval)
        print("getting session")

        r = requests.get(f"https://photospicker.googleapis.com/v1/sessions/{session_id}", headers=headers)
        r_json = r.json()

        print(json.dumps(r_json))
        photos_selected = r_json["mediaItemsSet"]

    service = build("photospicker", "v1", credentials=creds, static_discovery=False)

    # Retrieve the documents contents from the Docs service.
    media_items = service.mediaItems().list(sessionId=session_id).execute()

    print(f"Got {len(media_items['mediaItems'])} media items back. Downloading...")

    for media_item in media_items["mediaItems"]:
        print(f"Processing {json.dumps(media_item)}")
        base_url = media_item['mediaFile']['baseUrl']

        if media_item["type"] == "PHOTO":
          resource_url = f"{base_url}=d"
        elif media_item["type"] == "VIDEO":
          resource_url = f"{base_url}=dv"
        else:
          print(f"Invalid media item type {media_item['type']}")
          continue

        print(f"Will download base url {resource_url}")
        r = requests.get(resource_url, headers=headers)

        with open(f"{media_item['id']}.jpg", 'wb') as fd:
            for chunk in r.iter_content(chunk_size=128):
                fd.write(chunk)

    headers = {
        "Authorization": f"Bearer {creds.token}"
    }
    r = requests.delete(f"https://photospicker.googleapis.com/v1/sessions/{session_id}", headers=headers)
    print(f"Delete old session response status {r.status_code}")

  except HttpError as err:
    print(err)


if __name__ == "__main__":
  main()