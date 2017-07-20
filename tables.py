from flask_table import Table, Col

class CollectionTable(Table):
    title = Col('Title')
    artist = Col('Artist')
    year = Col('year')

class CollectionItem(object):
    def __init__(self, title, artist, year):
        self.title = title
        self.artist = artist
        self.year = year

# items = [Item('Tim', '1989'), Item('Moondance', '1969')]
# table = ItemTable(items)
