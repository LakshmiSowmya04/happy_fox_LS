import pytest
import json
from unittest.mock import patch, MagicMock, mock_open
from datetime import datetime, timezone 
import process_emails

# This is the fake JSON data we will pretend is in rules.json
FAKE_RULES_JSON = """
[
  {
    "rule_name": "Flag Invoices",
    "predicate": "Any",
    "conditions": [
      { "field": "Subject", "predicate": "contains", "value": "Invoice" }
    ],
    "actions": [
      { "action": "Mark as Unread" }
    ]
  }
]
"""

# This test simulates the entire email processing flow by mocking Gmail authentication, 
# the database, and rules, and verifies that a matching rule correctly triggers the execute_actions function with expected arguments.
@patch('process_emails.get_emails_from_db')
@patch('process_emails.execute_actions')
@patch('process_emails.authenticate_gmail_modify')
@patch("builtins.open", new_callable=mock_open, read_data=FAKE_RULES_JSON)
def test_full_processing_flow(mock_file, mock_auth, mock_execute_actions, mock_get_db):
    """
    Tests the entire processing flow with a mocked database and rules file.
    """
    fake_email = {
        'message_id': '12345',
        'subject': 'Your Invoice is here',
        'from_address': 'test@example.com',
        'received_date': datetime.now(timezone.utc)
    }
    mock_get_db.return_value = [fake_email]
    
    mock_service = MagicMock()
    mock_auth.return_value = mock_service

    process_emails.main()

    mock_execute_actions.assert_called_once()
    expected_actions = [{"action": "Mark as Unread"}]
    mock_execute_actions.assert_called_with(mock_service, '12345', expected_actions)