from collections import Counter

from app import mongo
from app.collection.tables import CollectionItem
from config import BREAKPOINT_VALUE

from app.models import RecordModel

def get_items(user, for_table=True, add_breakpoints=False):
    all_records = user['records']
    record_dict = {i['id']: [i['count'], i['date_added']] for i in all_records}
    col_list = []
    if len(record_dict) > 0:
        records = mongo.db.records.find({'_id': {'$in': list(record_dict.keys())}})
        for record in records:
            date = record_dict[record['_id']][1]

            if add_breakpoints:
                genres = ', '.join([i + BREAKPOINT_VALUE for i in record['genres']])
                styles = ', '.join([i + BREAKPOINT_VALUE for i in record['styles']])
            else:
                genres = ', '.join(record['genres'])
                styles = ', '.join(record['styles'])

            x = CollectionItem(record['title'],
                               record['artists'][0],
                               record['year'],
                               genres,
                               styles,
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

def convert_df_to_items_and_sort(df, user, sort_on=None, ascending=False):
    '''sort_on: can be list of keys'''
    if sort_on:
        df = df.sort_values(sort_on, ascending=ascending)

    col_list = []
    for idx, row in df.iterrows():
        album_id = mongo.db.records.find_one({'title': row['Title']}, {'_id': 1})
        col_list.append(CollectionItem(row['Title'], row['Artist'], row['Year'], row['Genre'], row['Style'],
                         row['TimesPlayed'], row['DateAdded'], album_id['_id'], user['user']))
    return col_list


def get_most_common_genres(df):

    def remove_start(s):
        if s[:2] == ', ':
            return s[2:]
        return s

    df = df[df.TimesPlayed > 0]
    genres = df.Genre.str.split('|')
    genres = [item for sublist in genres.values for item in sublist]
    genres = [remove_start(i) for i in genres if i != '' or i != '']
    return Counter(genres).most_common()

def shorten_string(s):
    if '&' in s and len(s) >= 12:
        split = s.split('&')
        s = [i[0] for i in split]
        return '&'.join(s)
    elif len(s) >= 12:
        return s[:7] + '...'
    return s


