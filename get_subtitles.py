import pandas as pd
import requests
from youtube_transcript_api import YouTubeTranscriptApi
from youtube_transcript_api._errors import TranscriptsDisabled


API_KEY = 'Enter your api key here'
# Specify playlist ID, the value below is for all YMH episodes
playlist_id = 'PL-i3EV1v5hLd9H1p2wT5ZD8alEY0EmxYD'


def get_captions_page(response):
    captions = []
    for item in response['items']:
        video_id = item['snippet']['resourceId']['videoId']
        print(video_id)
        try:
            caption = YouTubeTranscriptApi.get_transcript(video_id)
        except TranscriptsDisabled as e:
            print(e)
            continue
        df = pd.DataFrame(caption)
        df['video_title'] = item['snippet']['title']
        df['date'] = item['snippet']['publishedAt']
        df['video_id'] = video_id
        df['playlist_id'] = playlist_id
        captions.append(df)
    return captions


base_url = 'https://www.googleapis.com/youtube/v3/playlistItems?part=snippet%2C+id'
r = requests.get(f'{base_url}&playlistId={playlist_id}&maxResults=50&key={API_KEY}').json()
captions = [get_captions_page(r)]
while 'nextPageToken' in r.keys():
    r = requests.get(
        f'{base_url}&playlistId={playlist_id}&maxResults=50&pageToken={r["nextPageToken"]}&key={API_KEY}'
    ).json()
    captions.append(get_captions_page(r))

flat_list = [item for sublist in captions for item in sublist]
df_captions = pd.concat(flat_list, ignore_index=True)
print(df_captions.shape)
df_captions['date'] = pd.to_datetime(df_captions['date'])
df_captions.to_csv('ymh_captions.csv', sep='|')
