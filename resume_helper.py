"""Resume Helper

From a default resume in GDrive, make a copy of the file renamed to include a role modifier. For example, if applying to
"Role X" and "Company Y", it would create a copy of the template file with a new name of "Resume - Company X - Role Y".

Code _borrowed_ heavily from https://developers.google.com/docs/api/quickstart/python.

_Caveat Emptor_: I haven't tested by special characters in the modifier may cause issues.

Set up: Follow the instructions for setting up an application and downloading a credentials.json in the google link above.

@todo Add handling for a cover letter also
@todo Define a text delimiter and replace text in the resume and cover letter with a text string
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
RESUME_DOCUMENT_ID = "1aZAY2BK0lA7cDR7V6u1UG7__xsC1d_5sigXj9PO1-yc"
COVERLETTER_DOCUMENT_ID = "1fo-3MXG_Nitq1T5WQV-FHN1ePp2rVGBrZSYNWI_L6x4"


def main(company_name: str, role_name: str):
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

    # todo: Refactor this to be DRY
    new_resume_name = _build_document_name('resume', company_name, role_name)
    resume = _copy_document(service, RESUME_DOCUMENT_ID, new_resume_name)

    resume_file_url = f"https://docs.google.com/document/d/{resume.get('id')}/edit"

    new_coverletter_name = _build_document_name('coverletter', company_name, role_name)
    coverletter = _copy_document(service, COVERLETTER_DOCUMENT_ID, new_coverletter_name)

    coverletter_file_url = f"https://docs.google.com/document/d/{coverletter.get('id')}/edit"

    print(f"The new resume is: {resume_file_url}")
    print(f"The new cover letter is: {coverletter_file_url}")
    # end refactor todo

  except HttpError as err:
    print(err)

def _copy_document(service, document_id: str, new_name: str):
  new_document = service.files().copy(fileId=document_id, body={'name': new_name} ).execute()

  return new_document

def _parse_args() -> argparse.Namespace:
    """
    Parse input arguments.

    :return: argparse.Namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('company_name',
                        help="The company name to be added to the title of the new file."
                        )
    
    parser.add_argument('role_name',
                        help="The role name to be added to the title of the new file."
                        )

    return parser.parse_args()

def _build_document_name(document_type: str, company_name: str, role_name: str) -> str:
    match document_type:
      case 'resume':
        type_name = 'Resume'
      case 'coverletter':
        type_name = 'Cover Letter'
      case _:
        raise ValueError(f'Document Type must be one of resume or coverletter. Got {document_type}')
    
    document_name = f'{type_name} - {company_name} - {role_name}'

    return document_name

if __name__ == "__main__":
  company_name = vars(_parse_args()).pop('company_name')
  role_name = vars(_parse_args()).pop('role_name')

  main(company_name, role_name)