from app import app

import pylast

import sys
import datetime


def get_time(current_time, duration):
    time_split = duration.split(':')
    minute, second = int(time_split[0]), int(time_split[1])
    lfm_timestamp_datetime = current_time + datetime.timedelta(0, minute, second)
    return lfm_timestamp_datetime

def scrobble_album(record, user):
    try:
        lastfm_client = pylast.LastFMNetwork(api_key=app.config['LASTFM_API_KEY'],
                                             api_secret=app.config['LASTFM_API_SECRET'],
                                             username=user['lastfm_username'], password_hash=user['lastfm_password'])
        artist = record['artists'][0]
        lfm_timestamp_datetime = datetime.datetime.now()
        for track in record['track_data']:
            if track['duration'] != '':
                track_length = track['duration']
                lfm_timestamp_datetime = get_time(lfm_timestamp_datetime, track_length)
            lfm_timestamp = (lfm_timestamp_datetime - datetime.datetime.utcfromtimestamp(0)).total_seconds()
            lastfm_client.scrobble(artist=artist, title=track['title'], timestamp=lfm_timestamp)
    except:
        print(sys.exc_info()[:2])