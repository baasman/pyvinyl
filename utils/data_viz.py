from app import mongo, app
from tables.collection_table import CollectionItem

from collections import Counter


def get_items(user, for_table=True):
    all_records = user['records']
    record_dict = {i['id']: [i['count'], i['date_added']] for i in all_records}
    col_list = []
    if len(record_dict) > 0:
        records = mongo.db.records.find({'_id': {'$in': list(record_dict.keys())}})
        for record in records:
            date = record_dict[record['_id']][1]
            x = CollectionItem(record['title'],
                               record['artists'][0],
                               record['year'],
                               ', '.join(record['genres']),
                               ', '.join(record['styles']),
                               record_dict[record['_id']][0],
                               date,
                               record['_id'],
                               user['user'])
            if for_table:
                col_list.append(x)
            else:
                col_list.append([x.title, x.artist, x.year, x.genre, x.style, x.times_played,
                                x.date_added])
    return col_list

def get_most_common_genres(df):
    df.Genre = df.Genre.str.replace(' ', '')
    df.Genre = df.Genre .str.replace(',&', '&')
    genres = df.Genre.str.split(',')
    genres = [item for sublist in genres.values for item in sublist]
    c = Counter(genres).most_common()
    return c

