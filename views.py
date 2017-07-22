from app import *
from user_management import User
from forms import LoginForm, RegistrationForm, DiscogsValidationForm, AddRecordForm
from tables import CollectionTable, CollectionItem
from flask import request, redirect, render_template, flash, url_for, send_from_directory
from flask_login import login_user, logout_user, login_required

import discogs_client
from bson import Binary

import sys
import datetime
import requests
import io
import os
from PIL import Image


@login_manager.user_loader
def load_user(user):
    user = mongo.db.users.find_one({'user': user})
    if user:
        return User(username=user['user'])
    else:
        return None




@app.route('/collection/<username>')
@login_required
def collection(username):
    sort = request.args.get('sort')
    reverse = (request.args.get('direction', 'asc') == 'desc')
    user = mongo.db.users.find_one({'user': username})
    all_records = user['records']
    record_dict = {i['id']: [i['count'], i['date_added']] for i in all_records}
    if len(record_dict) > 0:
        records = mongo.db.records.find({'_id': {'$in': list(record_dict.keys())}})
        items = []
        for record in records:
            date = record_dict[record['_id']][1]
            items.append(CollectionItem(record['title'],
                                        record['artists'][0],
                                        record['year'],
                                        ', '.join(record['styles']),
                                        ', '.join(record['genres']),
                                        record_dict[record['_id']][0],
                                        date,
                                        record['_id']))
        table = CollectionTable(items)
    else:
        table = None
    return render_template('collection.html', username=username, user=user,
                           client=dclient, table=table)

@app.route('/discogs_setup/<username>', methods=['GET', 'POST'])
@login_required
def discogs_setup(username):
    args = dict(request.args)
    token, secret, url = args['tokens']
    n = mongo.db.users.update({'user': username},
                              {'$set': {'discogs_info':
                                            {'token': token,
                                            'secret': secret}}})
    form = DiscogsValidationForm()
    if request.method == 'POST':
        oath_code = form.code.data
        access_token, access_secret = dclient.get_access_token(oath_code)
        n = mongo.db.users.update({'user': username},
                                  {'$set': {'discogs_info.oauth_code': oath_code,
                                            'discogs_info.access_token': access_token,
                                            'discogs_info.access_secret': access_secret}})
        return redirect(url_for('collection', username=username))
    return render_template('discogs_signup.html', url=url, form=form)

@app.route('/add_record/', methods=['GET', 'POST'])
@login_required
def add_record():
    args = dict(request.args)
    username = args['username'][0]
    user = mongo.db.users.find_one({'user': username})
    form = AddRecordForm()
    if request.method == 'POST':
        discogs_id = int(form.discogs_id.data)
        if mongo.db.users.find_one({'user': username,
                                    'records': {'$in': [discogs_id]}}) is not None:
            flash('Album already in collection')
            return redirect(url_for('collection', username=username, user=user))
        else:
            n = mongo.db.users.update({'user': username}, {'$addToSet': {'records':
                                                                             {'id': discogs_id,
                                                                              'count': 0,
                                                                              'date_added': datetime.datetime.now()}}})
            record = mongo.db.records.find_one({'_id': discogs_id})
            if record is None:
                album = dclient.release(discogs_id)
                try:
                    tracklist = album.tracklist
                    artists = album.artists
                    genres = album.genres
                    styles = album.styles
                    image = album.images[0]
                except discogs_client.exceptions.HTTPError:
                    flash('Could not find release on discogs. Double check the release id')
                    return redirect(url_for('add_record', username=username))
                try:
                    image_bytes = requests.get(image['resource_url']).content
                    image_binary = Binary(image_bytes)
                    n = mongo.db.records.insert_one({'_id': discogs_id,
                                                     'year': int(album.year),
                                                     'title': album.title,
                                                     'artists': [i.name for i in artists],
                                                     'tracks': [i.title for i in tracklist],
                                                     'genres': genres,
                                                     'styles': styles,
                                                     'image': image,
                                                     'image_binary': image_binary})
                except:
                    print(sys.exc_info()[:2])
            return redirect(url_for('collection', username=username,
                                    user=mongo.db.users.find_one({'user': username})))
    return render_template('add_record.html', form=form)


@app.route('/album/<int:album_id>')
def album_page(album_id):
    record = mongo.db.records.find_one({'_id': album_id})
    image_binary = record['image_binary']
    filename = 'temp_image%d.jpeg' % album_id
    upload_filename = os.path.join(app.static_folder, 'tmp', filename)
    with open(upload_filename, 'wb') as f:
        f.write(image_binary)
    return render_template('album_page.html', record=record, filename=filename)


@app.route('/')
def home():
    return render_template('home.html')


@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if request.method == 'POST': # and form.validate_on_submit():
        user = mongo.db.users.find_one({'user': form.user.data})
        if user and User.validate_login(user['password_hash'], form.password.data):
            user_obj = User(user['user'])
            login_user(user_obj)
            flash('Logged in successfully. Happy scrobbling', category='success')
            return redirect(url_for('collection', username=user['user']))
        else:
            flash('Password does not match username', category='error')
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():
    reg_form = RegistrationForm()
    if request.method == 'POST' and reg_form.validate_on_submit():
        user_obj = User(email=reg_form.email.data,
                        username=reg_form.username.data,
                        discogs_user=reg_form.discogs_user.data)
        user_obj.set_password(reg_form.password.data)
        try:
            n = mongo.db.users.insert_one({'user': user_obj.username,
                                          'email': user_obj.email,
                                          'password_hash': user_obj.password_hash,
                                           'discogs_user': user_obj.discogs_user,
                                           'records': [],
                                           'discogs_info': {'oath_token': None,
                                                            'token': None,
                                                            'secret': None}})
            login_user(user_obj)
            flash('Thanks for registering')
            return redirect(url_for('collection', username=user_obj.username))
        except:
            print(sys.exc_info()[:2])
    return render_template('register.html', form=reg_form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))
