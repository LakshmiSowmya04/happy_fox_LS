# from google_auth_oauthlib.flow import InstalledAppFlow
# from googleapiclient.discovery import build

# # SCOPES define the access level — here we want read/write access to Gmail
# SCOPES = ['https://www.googleapis.com/auth/gmail.modify']

# def validate_credentials():
#     try:
#         # Load OAuth flow
#         flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
#         creds = flow.run_local_server(port=0)

#         # Build Gmail service
#         service = build('gmail', 'v1', credentials=creds)

#         # Call Gmail API to get profile
#         profile = service.users().getProfile(userId='me').execute()

#         # Print user's Gmail ID and message count
#         print("Credentials are valid!")
#         print(f"Email Address: {profile.get('emailAddress')}")
#         print(f"Total Messages: {profile.get('messagesTotal')}")
#         print(f"Threads Total: {profile.get('threadsTotal')}")

#     except Exception as e:
#         print("Error validating credentials:")
#         print(e)

# if __name__ == '__main__':
#     validate_credentials()
