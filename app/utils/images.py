from flask import current_app as app

from app import mongo

import os

def upload_image(record, username):
    fname = 'temp_image%s.jpeg' % record['_id']
    upload_filename = os.path.join(app.static_folder, 'tmp', fname)
    if not os.path.exists(upload_filename):
        with open(upload_filename, 'wb') as f:
            f.write(record['image_binary'])
            n = mongo.db.users.update({'user': username},
                                      {'$push': {'tmp_files': fname}})
    return fname