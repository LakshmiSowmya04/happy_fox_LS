The goal is to create a standalone Python application that fetches emails from a Gmail account, stores them in a database, and then processes them based on a set of rules defined in a JSON file. The application will be divided into two main scripts: one for fetching emails and another for processing them.

"process_emails.py" is a file which will do operations on emails stored in databse.
"database_setup.py" is a file which will setup the postgresql database setup
"token.json" is file which 
```
happy_happy/
├── config.py # Contains DB credentials (kept secret)
├── credentials.json # Gmail API client secrets (hidden)
├── token.json # OAuth access token (auto-generated, hidden)
├── database_setup.py # Creates 'email_db' and 'emails' table
├── fetch_emails.py # Fetches Gmail messages and stores in DB
├── process_emails.py # Applies rule-based actions on emails
├── rules.json # JSON file with your custom email rules
├── requirements.txt # Python dependencies
└── README.md # This file :)
```
---
## ⚙️ Setup Instructions
### 1. Clone the Repository
```bash
git clone https://github.com/your-username/happy_happy.git
cd happy_happy
python -m venv venv
# PowerShell:
.\venv\Scripts\Activate.ps1
# OR CMD:
venv\Scripts\activate.bat
```
```pip install -r requirements.txt```

## 📌 Gmail API Setup

1.Go to Google Cloud Console.

2.Create a project and enable the Gmail API.

3.Set up the OAuth consent screen (user type: external).

4.Create OAuth credentials → Choose Desktop App.

5.Download the credentials.json and place it in your root project folder.

6.When you run fetch_emails.py, you’ll be prompted to log in — a token.json will be generated.

##  Set Up the Database
Before running anything else:
 ```python database_setup.py```

=> In this project I have kept my PostgreSQL port number as 3306
=> Connect to PostgreSQL
=> Create email_db (if not exists)
=> Create the emails table

## 📥 Fetch Emails
```python fetch_emails.py```
This script will Connect to Gmail API ,Fetch message ID, sender, subject, date, and snippet and Save them to the emails table in PostgreSQL

```python process_emails.py```
This script will Process Emails Based on Rules from rules.json file

