"""Resume Helper

From a default resume in GDrive, make a copy of the file renamed to include a role modifier. For example, if applying to
"Role X" and "Company Y", it would create a copy of the template file with a new name of "Resume - Company X - Role Y".

Code _borrowed_ heavily from https://developers.google.com/docs/api/quickstart/python.

_Caveat Emptor_: I haven't tested by special characters in the modifier may cause issues.

Set up: Follow the instructions for setting up an application and downloading a credentials.json in the google link above.
"""

import argparse
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/drive"]

# The ID of base resume document.
DOCUMENT_ID = "1UqHEDcDvv-cL9t40dtMT0OYI4Z8hqpuPDPoV0llIDII"


def main(modifier: str):
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
    service = build("drive", "v3", credentials=creds)

    new_file_name = f"Resume - {modifier}"
    document = service.files().copy(fileId=DOCUMENT_ID, body={'name': new_file_name} ).execute()

    file_url = f"https://docs.google.com/document/d/{document.get('id')}/edit"

    print(f"The new document is: {file_url}")
  except HttpError as err:
    print(err)

def _parse_args() -> argparse.Namespace:
    """
    Parse input arguments.

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('company_role',
                        help="The company and role information to be added to the title of the new file."
                        )

    return parser.parse_args()


if __name__ == "__main__":
  file_modifier = vars(_parse_args()).pop('company_role')

  main(file_modifier)