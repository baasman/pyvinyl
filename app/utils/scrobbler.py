from app.models import User, Record, RecordPlay

import sys
import datetime


def get_time(current_time, duration):
    time_split = duration.split(':')
    minute, second = int(time_split[0]), int(time_split[1])
    lfm_timestamp_datetime = current_time + datetime.timedelta(seconds=(minute * 60 + second))
    return lfm_timestamp_datetime

def scrobble_album(client, record, current_time):
    try:
        artist = record['artists'][0]
        current_time = datetime.datetime.utcnow()
        for track in record['track_data']:
            if track['duration'] != '':
                track_length = track['duration']
                current_time = get_time(current_time, track_length)
                print(current_time)
            lfm_timestamp = (current_time - datetime.datetime.utcfromtimestamp(0)).total_seconds()
            client.scrobble(artist=artist, title=track['title'], timestamp=lfm_timestamp)
    except:
        print(sys.exc_info()[:2])


def update_stats(username, album_id, dt):
    n1 = User.objects(user=username, records__id=album_id).update(inc__records__S__count=1)
    n2 = Record.objects(_id=album_id).update(inc__total_plays=1)

    play = RecordPlay(user=username, date=dt)
    n3 = Record.objects(_id=album_id).update(push__plays=play)
