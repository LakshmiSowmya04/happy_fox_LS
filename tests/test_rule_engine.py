from datetime import datetime, timedelta, timezone
from process_emails import evaluate_condition

#this file contains unit tests for the rule engine in process_emails.py.It ensures process_emails.py file logic is reliable before processing actual emails
#Tests if "Phoenix" is found in the email subject.
def test_string_contains_pass():
    """Tests if the 'contains' predicate works for strings."""
    email = {'subject': 'Project Phoenix Update'}
    condition = {'field': 'Subject', 'predicate': 'contains', 'value': 'Phoenix'}
    assert evaluate_condition(email, condition) is True

#Tests if a wrong sender fails an equality check.
def test_string_equals_fail():
    """Tests if the 'equals' predicate fails correctly."""
    email = {'from_address': 'someone@example.com'}
    condition = {'field': 'From', 'predicate': 'equals', 'value': 'another@example.com'}
    assert evaluate_condition(email, condition) is False

#Checks if an email received 2 days ago is considered "less than 3 days old".
def test_date_less_than_pass():
    """Tests if the 'less_than' predicate for dates works correctly."""
    two_days_ago = datetime.now(timezone.utc) - timedelta(days=2)
    email = {'received_date': two_days_ago}
    # Rule: "is less than 3 days old"
    condition = {'field': 'Received Date', 'predicate': 'less_than', 'value': '3 days'}
    assert evaluate_condition(email, condition) is True

#Checks if an email received 10 days ago is "greater than 7 days old"
def test_date_greater_than_pass():
    """Tests if the 'greater_than' predicate for dates works correctly."""
    ten_days_ago = datetime.now(timezone.utc) - timedelta(days=10)
    email = {'received_date': ten_days_ago}
    # Rule: "is greater than 7 days old"
    condition = {'field': 'Received Date', 'predicate': 'greater_than', 'value': '7 days'}
    assert evaluate_condition(email, condition) is True