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

def get_channel_category(channel_choice):
    if channel_choice == '🟡top10countryrankings':
        return '#top10'
    elif channel_choice == '🔴Top10AnythingAndMore':
        return '#anythingtop10'
    else:
        raise ValueError(f"Unexpected channel choice: {channel_choice}")


from datetime import datetime, timedelta, time
from datetime import timezone
import csv
import pytz


def get_next_available_slot(last_upload_time):
    next_1_pm = datetime.combine(last_upload_time.date(), time(13))  # next 1 PM
    next_9_pm = datetime.combine(last_upload_time.date(), time(21))  # next 9 PM

    if last_upload_time < next_1_pm:
        return next_1_pm
    elif last_upload_time < next_9_pm:
        return next_9_pm
    else:
        # If it's already past 9 PM, schedule for 1 PM the next day
        return next_1_pm + timedelta(days=1)




def write_schedule_to_csv(schedule_time, video_title, csv_path):
    with open(csv_path, mode='a', newline='') as file:  # 'a' means append mode
        writer = csv.writer(file)
        writer.writerow([schedule_time.strftime('%Y-%m-%d %H:%M:%S'), video_title])  # write date and video title

def get_last_upload_time(csv_path):
    with open(csv_path, mode='r') as file:
        reader = csv.reader(file)
        rows = list(reader)  # convert reader to list

        if not rows:  # If empty/first time in the queue, return current time.
            print('Empty Schedule')
            print(datetime.now())
            return datetime.now()
        
        last_line = rows[-1]  # get the last line of the CSV
        last_upload_time = datetime.strptime(last_line[0], '%Y-%m-%d %H:%M:%S')  # convert string to datetime
        print('Last Upload time:', last_upload_time)
        return last_upload_time



def upload_video(youtube, filename, title, description, tags, publish_time):
    # First, make your datetime object "aware" of its timezone
    local_tz = pytz.timezone('US/Eastern')
    publish_time = local_tz.localize(publish_time)
    # Then, convert it to UTC
    publish_time_utc = publish_time.astimezone(timezone.utc)
    publish_time_str = publish_time_utc.isoformat("T").replace("+00:00", "") + "Z"# This will give time in format '2023-06-03T14:00:00Z')

    request = youtube.videos().insert(
        part="snippet,status",
        body={
            "snippet": {
                "categoryId": "24",
                "description": description,
                "title": title,
                "tags": tags,  # List of tags
            },
            "status": {
                "privacyStatus": "private",
                "publishAt": publish_time_str,
                "selfDeclaredMadeForKids": False,
                #"publishToSubscriptions": True
            }
        },
        media_body=MediaFileUpload(filename)
    )
    response = request.execute()
    return response



csv_path = r'C:\\Users\\lodos\\Desktop\\FilmForge Python\\FilmForge\\src\\files\\schedule.csv'

if __name__ == '__main__':
    last_upload_time = get_last_upload_time(csv_path)
    next_slot = get_next_available_slot(last_upload_time)
    print('Next available slot is:', next_slot)
    local_tz = pytz.timezone('US/Eastern')
    print('publish_time before localize:',next_slot)
    publish_time = local_tz.localize(next_slot)
    print('after localize:',publish_time)

    # Then, convert it to UTC
    publish_time_utc = publish_time.astimezone(timezone.utc)
    print('after astimezone:', publish_time_utc)
    print('publishAt before:',publish_time_utc.isoformat("T") + "Z")
    print('publishAt before 2:',publish_time_utc.isoformat("T") + "Z")
    publish_time_str = publish_time_utc.isoformat("T").replace("+00:00", "") + "Z"# This will give time in format '2023-06-03T14:00:00Z')
    print('publishAt new:', publish_time_str)