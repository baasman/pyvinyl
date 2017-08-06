from app import app, mongo, dclient, login_manager
from user_management import User
from forms.user_forms import LoginForm, RegistrationForm
from forms.misc_forms import DiscogsValidationForm, AddRecordForm, ScrobbleForm, AddTagForm
from tables.collection_table import CollectionTable, CollectionItem
from flask import request, redirect, render_template, flash, url_for, g
from flask_login import login_user, logout_user, login_required, current_user
from utils.scrobbler import scrobble_album
from utils.data_viz import get_items, get_most_common_genres


import discogs_client
from bson import Binary
import pandas as pd

import sys
import datetime
import requests
import os


@app.route('/<string:username>/explore', methods=['GET', 'POST'])
@login_required
def explore_collection(username):
    user = mongo.db.users.find_one({'user': username})
    df_list = get_items(user, for_table=False, add_breakpoints=True)
    df = pd.DataFrame(df_list, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    df.to_csv('temp2.csv', index=False)
    genres = get_most_common_genres(df)

    all_tags = list(mongo.db.users.aggregate([
        {'$match': {'user': username}},
        {'$unwind': '$tags'},
        {'$project': {'tags': 1}},
        {'$group': {'_id': '$tags.tag', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]))

    top_albums = df.sort_values('TimesPlayed', ascending=False)[['Title', 'TimesPlayed']].head(6)
    records = []
    for title in top_albums.Title.values:
        records.append(mongo.db.records.find_one({'title': title}))

    images_to_display = []
    for record in records:
        fname = 'temp_image%s.jpeg' % record['_id']
        upload_filename = os.path.join(app.static_folder, 'tmp', fname)
        if not os.path.exists(upload_filename):
            with open(upload_filename, 'wb') as f:
                f.write(record['image_binary'])
                n = mongo.db.users.update({'user': username},
                                          {'$push': {'tmp_files': fname}})
        n_plays_by_user = top_albums.loc[top_albums.Title == record['title'], 'TimesPlayed'].values[0]
        images_to_display.append((fname, record['_id'], n_plays_by_user))

    return render_template('explore_collection.html', filename=fname,
                           images_to_display=images_to_display, user=user,
                           most_common_genres=genres[:6],
                           most_common_tags=all_tags[:6])

@app.route('/<string:username>/explore/top_genres')
def top_genres(username):
    user = mongo.db.users.find_one({'user': username})
    df_list = get_items(user, for_table=False, add_breakpoints=True)
    df = pd.DataFrame(df_list, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    genres = get_most_common_genres(df)
    return render_template('top_genres.html', username=username, most_common_genres=genres)

@app.route('/<string:username>/explore/top_tags')
def top_tags(username):
    user = mongo.db.users.find_one({'user': username})
    all_tags = list(mongo.db.users.aggregate([
        {'$match': {'user': username}},
        {'$unwind': '$tags'},
        {'$project': {'tags': 1}},
        {'$group': {'_id': '$tags.tag', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]))
    return render_template('top_tags.html', username=username,
                           most_common_tags=all_tags)


@app.route('/<string:username>/explore/<string:genre>')
def top_in_genre(username, genre):
    records = mongo.db.records.find({'plays.user': username,
                                     'genres': genre})
    images_to_display = []
    for record in records:
        fname = 'temp_image%s.jpeg' % record['_id']
        upload_filename = os.path.join(app.static_folder, 'tmp', fname)
        if not os.path.exists(upload_filename):
            with open(upload_filename, 'wb') as f:
                f.write(record['image_binary'])
                n = mongo.db.users.update({'user': username},
                                          {'$push': {'tmp_files': fname}})
        images_to_display.append((fname, record['_id']))
    return render_template('albums_in_genre.html', images_to_display=images_to_display,
                           username=username, genre=genre)

@app.route('/<string:username>/explore/tags/<string:tag>')
def top_in_tag(username, tag):
    records = mongo.db.users.aggregate([
        {'$match': {'user': username}},
        {'$unwind': '$tags'},
        {'$project': {'tags': 1}},
        {'$match': {'tags.tag': tag}},
        {'$group': {'_id': '$tags.id'}}
    ])

    images_to_display = []
    for record in records:
        fname = 'temp_image%s.jpeg' % record['_id']
        upload_filename = os.path.join(app.static_folder, 'tmp', fname)
        if not os.path.exists(upload_filename):
            with open(upload_filename, 'wb') as f:
                f.write(record['image_binary'])
                n = mongo.db.users.update({'user': username},
                                          {'$push': {'tmp_files': fname}})
        images_to_display.append((fname, record['_id']))
    return render_template('albums_in_tag.html', images_to_display=images_to_display,
                           username=username, tag=tag)


@app.route('/<string:username>/explore/top_albums')
def top_albums(username):
    user = mongo.db.users.find_one({'user': username})
    df_list = get_items(user, for_table=False)
    df = pd.DataFrame(df_list, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    top_albums = df.sort_values('TimesPlayed', ascending=False)[['Title', 'TimesPlayed']]
    records = []
    for title in top_albums.Title.values:
        records.append(mongo.db.records.find_one({'title': title}))

    images_to_display = []
    for record in records:
        fname = 'temp_image%s.jpeg' % record['_id']
        upload_filename = os.path.join(app.static_folder, 'tmp', fname)
        if not os.path.exists(upload_filename):
            with open(upload_filename, 'wb') as f:
                f.write(record['image_binary'])
                n = mongo.db.users.update({'user': username},
                                          {'$push': {'tmp_files': fname}})
        n_plays_by_user = top_albums.loc[top_albums.Title == record['title'], 'TimesPlayed'].values[0]
        images_to_display.append((fname, record['_id'], n_plays_by_user))

    return render_template('top_albums.html', images_to_display=images_to_display,
                           user=user)


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
    items = get_items(user, for_table=True)
    items2 = get_items(user, for_table=False)
    df = pd.DataFrame(items2, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    if len(items) > 0:
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
    if request.method == 'POST' and form.validate_on_submit():
        if form.discogs_id.data:
            discogs_id = int(form.discogs_id.data)
        else:
            discogs_id = int(form.discogs_master_id.data)
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
                    app.logger.info()
                    flash('Could not find release on discogs. Double check the release id')
                    return redirect(url_for('add_record', username=username))
                try:
                    try:
                        image_bytes = requests.get(image['resource_url']).content
                        image_binary = Binary(image_bytes)
                    except:
                        image_binary = 'default_image'
                    artist_id = artists[0].id
                    n = mongo.db.records.insert_one({'_id': discogs_id,
                                                     'year': int(album.year),
                                                     'title': album.title,
                                                     'artists': [i.name for i in artists],
                                                     'tracks': [i.title for i in tracklist],
                                                     'genres': [i for i in genres],
                                                     'styles': [i for i in styles],
                                                     'image': image,
                                                     'image_binary': image_binary,
                                                     'track_data': [i.data for i in tracklist],
                                                     'total_plays': 0,
                                                     'plays': [],
                                                     'artist_id': artist_id})
                except:
                    print(sys.exc_info()[:2])
            return redirect(url_for('collection', username=username,
                                    user=mongo.db.users.find_one({'user': username})))
    return render_template('add_record.html', form=form)


@app.route('/user/<string:username>/album/<int:album_id>', methods=['GET', 'POST'])
def album_page(username, album_id):
    user = mongo.db.users.find_one({'user': username})
    record = mongo.db.records.find_one({'_id': album_id})
    image_binary = record['image_binary']
    filename = 'temp_image%d.jpeg' % album_id
    upload_filename = os.path.join(app.static_folder, 'tmp', filename)
    scrobble_form = ScrobbleForm()
    tag_form = AddTagForm()

    total_user_plays = mongo.db.users.find_one(
        {'user': username, 'records.id': album_id},
        {'_id': 0, 'records.$': 1}
    )

    if total_user_plays:
        total_user_plays = total_user_plays['records'][0]['count']
    else:
        total_user_plays = 0

    if not os.path.exists(upload_filename):
        with open(upload_filename, 'wb') as f:
            f.write(image_binary)
            n = mongo.db.users.update({'user': username},
                                      {'$push': {'tmp_files': filename}})

    if request.method == 'POST':

        # TODO: scrobble form should not be called if tag form field is empty
        if tag_form.submit.data and tag_form.validate_on_submit():
            tags = tag_form.tag.data
            if ',' in tags:
                tags = tags.replace(' ', '')
                tags = tags.split(',')
                for tag in tags:
                    exists = mongo.db.users.find_one({'user': username,
                                                      'tags': {'$elemMatch':
                                                                   {'tags.id': album_id,
                                                                    'tags.tag': tag}}})
                    if not exists:
                        n1 = mongo.db.users.update({'user': username},
                                                   {'$push': {'tags': {'tag': tag,
                                                                       'id': album_id}}})
                    else:
                        print('tag already exists for this album')
            else:
                exists = mongo.db.users.find_one({'user': username,
                                                  'tags': {'$elemMatch':
                                                               {'tags.id': album_id,
                                                                'tags.tag': tags}}})
                if not exists:
                    n1 = mongo.db.users.update({'user': username},
                                               {'$push': {'tags': {'tag': tags,
                                                               'id': album_id}}})
                else:
                    print('tag already exists for this album')

            return render_template('album_page.html', record=record, filename=filename,
                                   scrobble_form=scrobble_form, total_user_plays=total_user_plays,
                                   tag_form=tag_form)

        elif scrobble_form.submit.data and scrobble_form.validate_on_submit():
            dt = scrobble_form.play_date.data
            scrobble_album(record=record, user=user, current_time=dt)
            has_time = record['track_data'][0]['duration'] != ''
            n1 = mongo.db.users.update({'user': username,
                                       'records.id': album_id},
                                      {'$inc': {'records.$.count': 1}})
            n2 = mongo.db.records.update({'_id': album_id},
                                         {'$inc': {'total_plays': 1}})
            n3 = mongo.db.records.update({'_id': album_id},
                                         {'$push': {'plays': {'date': dt,
                                                              'user': username}}},
                                         upsert=True)
            return render_template('album_page.html', record=record, filename=filename,
                                   has_time=has_time, scrobble_form=scrobble_form,
                                   total_user_plays=total_user_plays, tag_form=tag_form)
    return render_template('album_page.html', record=record, filename=filename,
                           scrobble_form=scrobble_form, total_user_plays=total_user_plays,
                           tag_form=tag_form)


@app.route('/')
def home():
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
        fname = 'temp_image%s.jpeg' % record['_id']
        upload_filename = os.path.join(app.static_folder, 'tmp', fname)
        if not os.path.exists(upload_filename):
            with open(upload_filename, 'wb') as f:
                f.write(record['image_binary'])
                if username != 'anonymous':
                    n = mongo.db.users.update({'user': username},
                                              {'$push': {'tmp_files': fname}})
        images_to_display.append((fname, record['_id'], date))

    return render_template('home.html', images_to_display=images_to_display, user=user,
                           username=username)


@app.route('/about')
def about():
    return render_template('about.html', color='green')


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
                        lastfm_user=reg_form.lastfm_user.data,
                        lastfm_password=reg_form.lastfm_password.data)
        user_obj.set_password(reg_form.password.data)
        try:
            n = mongo.db.users.insert_one({'user': user_obj.username,
                                          'email': user_obj.email,
                                          'password_hash': user_obj.password_hash,
                                           'lastfm_username': user_obj.lastfm_user,
                                           'lastfm_password': user_obj.lastfm_password,
                                           'records': [],
                                           'tmp_files': [],
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
    username = request.args.get('username')
    tmp_files = mongo.db.users.find_one({'user': username}, {'tmp_files': 1})
    for file in tmp_files['tmp_files']:
        try:
            os.remove(os.path.join(app.static_folder, 'tmp', file))
        except:
            print(sys.exc_info()[:2])
    n = mongo.db.users.update({'user': username},
                              {'$set': {'tmp_files': []}})
    logout_user()
    return redirect(url_for('home'))
