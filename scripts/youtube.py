import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import os


SCOPES = ['https://www.googleapis.com/auth/youtube.upload',
          'https://www.googleapis.com/auth/youtube']


def authenticate_youtube(channel_choice):
    """Shows basic usage of the YouTube API.
    Lists the videos that are uploaded to the authenticated user's channel.
    """

    # The CLIENT_SECRET_FILE variable specifies the name of a file that contains
    # the OAuth 2.0 information for this application, including its client_id and
    # client_secret.

    if channel_choice == '🟡top10countryrankings':
        CLIENT_SECRET_FILE = os.environ['CLIENT_SECRET_FILE0']
        TOKEN_FILE = 'token_channel0.pickle'
    elif channel_choice == '🔴Top10AnythingAndMore':
        CLIENT_SECRET_FILE = os.environ['CLIENT_SECRET_FILE1']
        TOKEN_FILE = 'token_channel1.pickle'
    else:
        raise ValueError(f"Unexpected channel choice: {channel_choice}")

    creds = None
    # The file TOKEN_FILE stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CLIENT_SECRET_FILE, SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(TOKEN_FILE, 'wb') as token:
            pickle.dump(creds, token)

    return build('youtube', 'v3', credentials=creds)


def upload_video(youtube, filename, title, description, tags):
    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "22",
                "description": description,
                "title": title,
                "tags": tags,  # List of tags
                "madeForKids": False
            },
            "status": {
                "privacyStatus": "public",
            }
        },
        media_body=MediaFileUpload(filename)
    )
    response = request.execute()
    return response
