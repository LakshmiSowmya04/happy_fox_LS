import os.path
import json
from datetime import datetime, timedelta, timezone
import psycopg2
import psycopg2.extras
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import config  # centralized configuration file

#Authenticates with the Gmail API using modify scope from the config and returns a service client for performing email actions.
def authenticate_gmail_modify():
    """
    Authenticates with Gmail API using modify scopes from the config file.
    It's crucial to use the correct scopes for processing actions.
    """
    creds = None
    # Using TOKEN_FILE from config
    if os.path.exists(config.TOKEN_FILE):
        # Using SCOPES_READ_WRITE from config
        creds = Credentials.from_authorized_user_file(config.TOKEN_FILE, config.SCOPES_READ_WRITE)

    if not creds or not creds.valid:
        # Re-authenticate or refresh token if needed
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Using CREDENTIALS_FILE and SCOPES_READ_WRITE from config
            flow = InstalledAppFlow.from_client_secrets_file(config.CREDENTIALS_FILE, config.SCOPES_READ_WRITE)
            creds = flow.run_local_server(port=0)
        # Save the new token
        with open(config.TOKEN_FILE, 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

# reads mails from database 
def get_emails_from_db():
    """Fetches all emails from the PostgreSQL database using the DSN from config."""
    try:
        with psycopg2.connect(config.DB_DSN) as conn:
            with conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cursor:
                cursor.execute('SELECT * FROM emails')
                return cursor.fetchall()
    except psycopg2.Error as e:
        print(f"Database Error: Could not fetch emails. {e}")
        return []

# This function checks if the email matches the specified conditions in the rule.
def evaluate_condition(email, condition):
    """Evaluates a single rule condition against an email's data."""
    field = condition['field']
    predicate = condition['predicate']
    value = condition['value']
    field_map = {"From": "from_address", "Subject": "subject", "Message": "message_body", "Received Date": "received_date"}
    db_column = field_map.get(field)
    if not db_column or db_column not in email or email[db_column] is None:
        return False

    email_field_value = email[db_column]

    if field in ["From", "Subject", "Message"]:
        email_field_str = str(email_field_value).lower()
        value_str = str(value).lower()
        if predicate == "contains": return value_str in email_field_str
        if predicate == "does not contain": return value_str not in email_field_str
        if predicate == "equals": return value_str == email_field_str
        if predicate == "does not equal": return value_str != email_field_str
    elif field == "Received Date":
        email_date = email['received_date'].astimezone(timezone.utc)
        now = datetime.now(timezone.utc)
        num, unit = value.split()
        delta = timedelta(days=int(num) * 30) if "month" in unit else timedelta(days=int(num))
        if predicate == "less_than": return now - email_date < delta
        if predicate == "greater_than": return now - email_date > delta
    return False

# This function executes the actions defined in the rule on the specified email.
def execute_actions(service, message_id, actions):
    """Executes a list of actions (e.g., mark as read, move) on a given email."""
    # This function's logic is sound and does not need changes.
    labels = service.users().labels().list(userId='me').execute().get('labels', [])
    label_map = {l['name']: l['id'] for l in labels}
    body = {'addLabelIds': [], 'removeLabelIds': []}
    for action in actions:
        if action['action'] == "Mark as Read": body['removeLabelIds'].append('UNREAD')
        if action['action'] == "Mark as Unread": body['addLabelIds'].append('UNREAD')
        if action['action'] == "Move Message":
            label_name = action.get('value')
            if label_name in label_map:
                body['addLabelIds'].append(label_map[label_name])
                body['removeLabelIds'].append('INBOX')
            else:
                print(f"Warning: Label '{label_name}' not found. Cannot move message {message_id}.")
    if body['addLabelIds'] or body['removeLabelIds']:
        try:
            service.users().messages().modify(userId='me', id=message_id, body=body).execute()
            print(f"Actions executed for message {message_id}: {body}")
        except HttpError as error:
            print(f"API Error executing action on message {message_id}: {error}")

def main():
    """Main function to process emails based on rules defined in a JSON file."""
    print("Authenticating for processing...")
    # Using the dedicated modify-scope authentication function
    service = authenticate_gmail_modify()

    try:
        # Corrected: Using RULES_FILE from config
        with open(config.RULES_FILE_PATH) as f:
            rules = json.load(f)
    except FileNotFoundError:
        print(f"Error: Rules file not found at '{config.RULES_FILE_PATH}'. Please check your config.")
        return

    emails = get_emails_from_db()
    if not emails:
        print("No emails found in the local database to process.")
        return

    print(f"\nProcessing {len(emails)} emails against {len(rules)} rules...")

    for email in emails:
        for rule in rules:
            results = [evaluate_condition(email, cond) for cond in rule['conditions']]
            if (rule['predicate'] == "All" and all(results)) or \
               (rule['predicate'] == "Any" and any(results)):
                print(f"\nRule '{rule['rule_name']}' matched for email: '{email['subject']}'")
                execute_actions(service, email['message_id'], rule['actions'])
                # Once a rule matches, we stop processing this email and move to the next.
                break

if __name__ == '__main__':
    main()