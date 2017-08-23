from app import mongo

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
        current_time = datetime.datetime.now()
        for track in record['track_data']:
            if track['duration'] != '':
                track_length = track['duration']
                current_time = get_time(current_time, track_length)
                print(current_time)
            lfm_timestamp = (current_time - datetime.datetime.utcfromtimestamp(0)).total_seconds()
            # client.scrobble(artist=artist, title=track['title'], timestamp=lfm_timestamp)
    except:
        print(sys.exc_info()[:2])


def update_stats(username, album_id, dt):
    n1 = mongo.db.users.update({'user': username,
                                'records.id': album_id},
                               {'$inc': {'records.$.count': 1}})
    n2 = mongo.db.records.update({'_id': album_id},
                                 {'$inc': {'total_plays': 1}})
    n3 = mongo.db.records.update({'_id': album_id},
                                 {'$push': {'plays': {'date': dt,
                                                      'user': username}}},
                                 upsert=True)
    print(n1)
    print(n2)
    print(n3)