from uuid import uuid4
import os

from app import mongo, app
from tables.collection_table import CollectionItem

import matplotlib.pyplot as plt

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
                               ', '.join(record['styles']),
                               ', '.join(record['genres']),
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

def simple_hist(user, data, column):

    # p = plt.figure()
    # h = data[column].hist()
    uuid = uuid4()
    fname = '%s.png' % str(uuid)
    upload_filename = os.path.join(app.static_folder, 'tmp_viz', fname)
    # if not os.path.exists(upload_filename):
    #     with open(upload_filename, 'wb') as f:
    #         p.savefig(fname)
    #         n = mongo.db.users.update({'user': user['user']},
    #                                   {'$push': {'tmp_viz': fname}},
    #                                   upsert=True)
    return fname

def artist_record_plot(user, data):
    pass
