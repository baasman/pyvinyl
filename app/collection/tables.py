from flask_table import Table, LinkCol, Col, DatetimeCol
from flask import url_for

class CollectionTable(Table):
    title = LinkCol('Title', endpoint='collection.album_page',
                    url_kwargs={'album_id': 'album_id', 'username': 'username'},
                    attr='title')
    artist = Col('Artist')
    year = Col('Year')
    genre = Col('Genre')
    style = Col('Style')
    times_played = Col('Times Played')
    date_added = DatetimeCol('Date Added')
    html_attrs = {'class': 'table table-hover'}

    # allow_sort = True
    #
    # def sort_url(self, col_id, reverse=False):
    #     if reverse:
    #         direction = 'desc'
    #     else:
    #         direction = 'asc'
    #     return url_for('collection', sort=col_id, direction=direction)

class CollectionItem(object):
    def __init__(self, title, artist, year, genre, style,
                 times_played, date_added, album_id, username):
        self.title = title
        self.artist = artist
        self.year = year
        self.genre = genre
        self.style = style
        self.times_played = times_played
        self.date_added = date_added
        self.album_id = album_id
        self.username = username

    # def get_sorted_by(all_items, sort, reverse=False):
    #     return sorted(all_items,
    #                   key=lambda x: getattr(x, sort),
    #                   reverse=reverse)

