import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.send',
          'https://www.googleapis.com/auth/gmail.compose',
          'https://www.googleapis.com/auth/gmail.labels',
          'https://www.googleapis.com/auth/gmail.modify']


def authenticate():
    """Authenticate and return Gmail API credentials."""
    if os.path.exists('gmail_api/cs_gmail_cred/token.json'):
        creds = Credentials.from_authorized_user_file('gmail_api/cs_gmail_cred/token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('gmail_api/cs_gmail_cred/credentials.json', SCOPES)
        creds = flow.run_local_server(port=8080)  # Use fixed port 8080
        with open('gmail_api/cs_gmail_cred/token.json', 'w') as token:
            token.write(creds.to_json())

    if not creds.valid and creds.expired and creds.refresh_token:
        creds.refresh(Request())

    return creds




# creds = Credentials.from_authorized_user_file('gmail_api/cs_gmail_cred/token.json', SCOPES)