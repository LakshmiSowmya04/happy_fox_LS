import os.path
import base64
import psycopg2
from datetime import datetime
from dateutil import parser  
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config  # centralized configuration file

# Authenticates with the Gmail API using read/write scopes from the config and returns a service client for performing email actions.
def authenticate_gmail():
    """
    Authenticates with the Gmail API using settings from the config file.
    """
    creds = None
    # Corrected: Using TOKEN_FILE from config
    if os.path.exists(config.TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES_READ_WRITE)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Using CREDENTIALS_FILE from config
            flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.SCOPES_READ_WRITE)
            creds = flow.run_local_server(port=0)
        # Using TOKEN_FILE from config
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)


# stores emails from the PostgreSQL database
def store_email(message_id, from_address, subject, message_body, received_date):
    """
    Stores a single email into the PostgreSQL database using a 'with' statement
    for robust connection handling.
    """
    sql = """
        INSERT INTO emails (message_id, from_address, subject, message_body, received_date)
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (message_id) DO NOTHING;
    """
    try:
        # Using 'with' statement and proper DSN usage
        with psycopg2.connect(config.DB_DSN) as conn:
            with conn.cursor() as cursor:
                cursor.execute(sql, (message_id, from_address, subject, message_body, received_date))
                conn.commit()
    except psycopg2.Error as e:
        print(f"Database Error: Failed to store email {message_id}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred in store_email: {e}")

# Fetches emails from Gmail and stores them in the database
# This function uses the Gmail API to fetch emails based on the label and max results defined in config.py.
def main():
    """Fetches emails from Gmail and stores them in the database."""
    service = authenticate_gmail()
    try:
        # Using FETCH_LABEL and MAX_RESULTS from config
        response = service.users().messages().list(
            userId='me',
            labelIds=[config.FETCH_LABEL],
            maxResults=config.MAX_RESULTS
        ).execute()

        messages = response.get('messages', [])
        if not messages:
            print("No new messages found.")
            return

        print(f"Found {len(messages)} messages. Fetching details...")

        for msg in messages:
            msg_id = msg['id']
            try:
                txt = service.users().messages().get(userId='me', id=msg_id).execute()
                
                payload = txt['payload']
                headers = payload.get('headers', [])

                subject = next((d['value'] for d in headers if d['name'] == 'Subject'), 'No Subject')
                from_address = next((d['value'] for d in headers if d['name'] == 'From'), 'Unknown Sender')
                date_str = next((d['value'] for d in headers if d['name'] == 'Date'), None)

                # Using dateutil.parser for robust date handling
                try:
                    received_date = parser.parse(date_str)
                except (parser.ParserError, TypeError):
                    received_date = datetime.now().astimezone() # Fallback to current time

                message_body = ""
                if 'parts' in payload:
                    for part in payload['parts']:
                        if part['mimeType'] == 'text/plain' and 'data' in part['body']:
                            data = part['body']['data']
                            message_body = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')
                            break
                elif 'data' in payload['body']:
                    data = payload['body']['data']
                    message_body = base64.urlsafe_b64decode(data).decode('utf-8', 'ignore')

                store_email(msg_id, from_address, subject, message_body, received_date)
                print(f"Stored email from: {from_address} | Subject: {subject}")

            except HttpError as api_error:
                print(f"API error fetching message {msg_id}: {api_error}")
            except Exception as e:
                print(f"An error occurred processing message {msg_id}: {e}")

    except HttpError as error:
        print(f"A top-level Gmail API error occurred: {error}")

if __name__ == '__main__':
    # Reminder for the user to install the new dependency
    try:
        from dateutil import parser
    except ImportError:
        print("\n---")
        print("Warning: The 'python-dateutil' library is not installed.")
        print("Please run: pip install python-dateutil")
        print("---\n")
    main()