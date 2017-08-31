from flask_mongoengine import MongoEngine
import datetime

db = MongoEngine()

# User

class BaseUser(db.Document):

    meta = {
        'abstract': True
    }

    def check_permission(self):
        return True

    def add_record(self, id):
        record = UserRecord(id=id)
        self.update(add_to_set__records=record)

    def get_user(self, username):
        return self.objects.get(user=username)


class UserRecord(db.EmbeddedDocument):
    date_added = db.DateTimeField(default=datetime.datetime.now())
    id = db.IntField(required=True)
    count = db.IntField(default=0)


class UserTag(db.EmbeddedDocument):
    id = db.IntField(required=True)
    tag = db.StringField()


class User(BaseUser):
    email = db.StringField(unique=True)
    user = db.StringField(required=True, unique=True, max_length=40)
    lastfm_username = db.StringField()
    lastfm_password = db.StringField()
    records = db.ListField(db.EmbeddedDocumentField(UserRecord))
    tags = db.ListField(db.EmbeddedDocumentField(UserTag))
    tmp_files = db.ListField(db.StringField())
    lfm_is_authenticated = db.BooleanField(default=False)
    lastfm_token_url = db.StringField()

    def __str__(self):
        return 'user=%s' % self.user

    meta = {
        'allow_inheritance': True
    }

# Record

class BaseRecord(db.Document):

    meta = {
        'abstract': True
    }

    def get_record(self, id):
        return self.objects.get(_id=id)


class RecordPlay(db.EmbeddedDocument):
    date = db.DateTimeField()
    user = db.StringField()

class Record(BaseRecord):

    _id = db.IntField()
    artists = db.ListField()
    year = db.IntField()
    total_plays = db.IntField(default=0)
    styles = db.ListField()
    genres = db.ListField()
    track_data = db.ListField(db.DictField())
    tracks = db.ListField()
    artist_id = db.IntField()
    title = db.StringField()
    plays = db.ListField(db.EmbeddedDocumentField(RecordPlay))
    image_binary = db.BinaryField()

    def __str__(self):
        return '_id=%d, record=%s' % (self._id, self.title)


if __name__ == '__main__':

    record = UserRecord(id=432343)
    tag = UserTag(id=432343, tag='sensual')
    boudey = User(email='boudeyz@gmail.com',
                  user='boudey',
                  lastfm_username='boudey'
                  )
    boudey.save()
    boudey.add_record(id=432432)

    rec = Record(_id=34242342, artists=['mccoy', 'coltrane'])



