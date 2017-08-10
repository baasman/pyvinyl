from flask import render_template
import pandas as pd

from app import mongo

from utils.data_viz import get_items, get_most_common_genres

from . import explore

from utils.images import upload_image


@explore.route('/<string:username>/explore/top_genres')
def top_genres(username):
    user = mongo.db.users.find_one({'user': username})
    df_list = get_items(user, for_table=False, add_breakpoints=True)
    df = pd.DataFrame(df_list, columns=['Title', 'Artist', 'Year', 'Genre', 'Style',
                                        'TimesPlayed', 'DateAdded'])
    genres = get_most_common_genres(df)
    return render_template('explore/top_genres.html', username=username, most_common_genres=genres)

@explore.route('/<string:username>/explore/top_tags')
def top_tags(username):
    user = mongo.db.users.find_one({'user': username})
    all_tags = list(mongo.db.users.aggregate([
        {'$match': {'user': username}},
        {'$unwind': '$tags'},
        {'$project': {'tags': 1}},
        {'$group': {'_id': '$tags.tag', 'count': {'$sum': 1}}},
        {'$sort': {'count': -1}}
    ]))
    return render_template('explore/top_tags.html', user=user,
                           most_common_tags=all_tags)


@explore.route('/<string:username>/explore/<string:genre>')
def top_in_genre(username, genre):
    records = mongo.db.records.find({'plays.user': username,
                                     'genres': genre})
    images_to_display = []
    for record in records:
        fname = upload_image(record, username)
        images_to_display.append((fname, record['_id']))
    return render_template('explore/albums_in_genre.html', images_to_display=images_to_display,
                           username=username, genre=genre)

@explore.route('/<string:username>/explore/tags/<string:tag>')
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
        fname = upload_image(record, username)
        images_to_display.append((fname, record['_id']))
    return render_template('explore/albums_in_tag.html', images_to_display=images_to_display,
                           username=username, tag=tag)


@explore.route('/<string:username>/explore/top_albums')
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
        fname = upload_image(record, username)
        n_plays_by_user = top_albums.loc[top_albums.Title == record['title'], 'TimesPlayed'].values[0]
        images_to_display.append((fname, record['_id'], n_plays_by_user))

    return render_template('explore/top_albums.html', images_to_display=images_to_display,
                           user=user)