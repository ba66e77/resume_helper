"""Resume Helper

@todo Add a --fetch option which will instead download the files from Google as PDF and store them in the local file system.
"""

import argparse
import datetime
import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build, Resource
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.json.
SCOPES = [
  "https://www.googleapis.com/auth/drive", # drive scope for copying files
  "https://www.googleapis.com/auth/documents" # document scope for editing files
]

# The ID of base resume document.
RESUME_DOCUMENT_ID = "1aZAY2BK0lA7cDR7V6u1UG7__xsC1d_5sigXj9PO1-yc"
COVERLETTER_DOCUMENT_ID = "1fo-3MXG_Nitq1T5WQV-FHN1ePp2rVGBrZSYNWI_L6x4"

def _get_credentials(token_file_path: str = "token.json", credentials_file_path: str = "credentials.json") -> Credentials:
  creds = None

  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
  if os.path.exists(token_file_path):
    creds = Credentials.from_authorized_user_file(token_file_path, SCOPES)

  # If there are no (valid) credentials available, let the user log in.
  if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
      creds.refresh(Request())
    else:
      flow = InstalledAppFlow.from_client_secrets_file(
          credentials_file_path, SCOPES
      )
      creds = flow.run_local_server(port=0)

    # Save the credentials for the next run
    with open(token_file_path, "w") as token:
      token.write(creds.to_json())

  return creds

def _build_document_url(document_id: str) -> str:
  return f"https://docs.google.com/document/d/{document_id}/edit"

def main(company_name: str, role_name: str) -> None:
  """Shows basic usage of the Docs API.
  Prints the title of a sample document.

  """
  creds = _get_credentials()

  try:
    drive_service = build("drive", "v3", credentials=creds)
    document_service = build('docs', "v1", credentials=creds)

    # todo: refactor for DRY
    # todo: encapsulate this
    new_resume_name = _build_document_name('resume', company_name, role_name)
    resume = _copy_document(drive_service, RESUME_DOCUMENT_ID, new_resume_name)

    resume_id = resume.get('id')
    resume_file_url = _build_document_url(resume_id)
    # end encapsulate todo

    new_coverletter_name = _build_document_name('coverletter', company_name, role_name)
    coverletter = _copy_document(drive_service, COVERLETTER_DOCUMENT_ID, new_coverletter_name)

    coverletter_id = coverletter.get('id')
    coverletter_file_url = _build_document_url(coverletter_id)

    print(f"The new resume is: {resume_file_url}")
    print(f"The new cover letter is: {coverletter_file_url}")
    # end refactor todo
  
    date = datetime.datetime.now().strftime('%Y-%m-%d')

    for document in [coverletter_id, resume_id]:
      _replace_text(document_service, document, company_name, role_name, date)

  except HttpError as err:
    print(err)

def _replace_text(document_service: Resource, document_id: str, company_name: str, role_name: str, date_string: str) -> dict:
  """
  cover letter fields: {{date}}, {{title}}, {{company_name}}

  resume fields: {{title}}

  @todo: pass in a dict of replacement keys and replacement values, to be more reusable.
  """

  requests = [
         {
            'replaceAllText': {
                'containsText': {
                    'text': '{{title}}',
                    'matchCase':  'true'
                },
                'replaceText': role_name,
            }
          },
          {
            'replaceAllText': {
                'containsText': {
                    'text': '{{company_name}}',
                    'matchCase':  'true'
                },
                'replaceText': company_name,
            }
          },
          {
            'replaceAllText': {
                'containsText': {
                    'text': '{{date}}',
                    'matchCase':  'true'
                },
                'replaceText': date_string,
            }
          }
  ]
  
  result = document_service.documents().batchUpdate(
          documentId=document_id, 
          body={'requests': requests}
        ).execute()
  
  return result

def _copy_document(service: Resource, document_id: str, new_name: str) -> dict:
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