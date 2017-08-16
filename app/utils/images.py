from flask import current_app as capp

from app import mongo

import os


def upload_image(record, username):
    if record['image_binary'] != 'default_image':
        fname = 'temp_image%s.jpeg' % record['_id']
        upload_filename = os.path.join(capp.static_folder, 'tmp', fname)
        if not os.path.exists(upload_filename):
            with open(upload_filename, 'wb') as f:
                f.write(record['image_binary'])
                if username != 'anonymous':
                    n = mongo.db.users.update({'user': username},
                                              {'$push': {'tmp_files': fname}})
    else:
        fname = 'use_default'
    return fname