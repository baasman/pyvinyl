from flask import render_template, redirect, url_for
from flask import current_app as capp
from flask_login import current_user

from . import home
from app import mongo

import os

@home.route('/')
def homepage():
    try:
        username = current_user.username
        user = mongo.db.users.find_one({'user': username})
    except AttributeError:
        username = 'anonymous'
        user = None

    unwind = {'$unwind': '$plays'}
    project = {'$project': {'played': '$plays.date',
                            'album_name': '$title',
                            'image_binary': 1,
                            '_id': 1}}
    sort = {'$sort': {'played': -1}}
    limit = {'$limit': 6}
    pipeline = [unwind, project, sort, limit]
    recent_records = mongo.db.records.aggregate(pipeline)
    images_to_display = []
    for record in recent_records:
        date = record['played'].strftime('%b-%d %H:%M')
        if record['image_binary'] != 'default_image':
            fname = 'temp_image%s.jpeg' % record['_id']
            upload_filename = os.path.join(capp.static_folder, 'tmp', fname)
            if not os.path.exists(upload_filename):
                with open(upload_filename, 'wb') as f:
                    print(record['_id'])
                    f.write(record['image_binary'])
                    if username != 'anonymous':
                        n = mongo.db.users.update({'user': username},
                                                  {'$push': {'tmp_files': fname}})
        else:
            fname = 'use_default'
        images_to_display.append((fname, record['_id'], date))

    return render_template('home/home.html', images_to_display=images_to_display, user=user,
                           username=username)

@home.route('/about')
def about():
    return render_template('home/about.html', color='green')
