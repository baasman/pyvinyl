from flask_mongoengine import MongoEngine
from werkzeug.security import generate_password_hash, check_password_hash
import pylast
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
    password_hash = db.StringField()
    lastfm_username = db.StringField()
    lastfm_password = db.StringField()
    records = db.ListField(db.EmbeddedDocumentField(UserRecord))
    tags = db.ListField(db.EmbeddedDocumentField(UserTag))
    tmp_files = db.ListField(db.StringField())
    lfm_is_authenticated = db.BooleanField(default=False)
    lastfm_token_url = db.StringField()
    lfm_session_key = db.StringField()

    @property
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.user

    def generate_lfm_hash(self, password):
        return pylast.md5(password)

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)

    def set_password(self, password):
        return generate_password_hash(password)


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


class RecordPlay(db.EmbeddedDocument):
    date = db.DateTimeField()
    user = db.StringField()

class Record(BaseRecord):
    _id = db.IntField()
    artists = db.ListField(db.StringField())
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

    import mongoengine
    # mongoengine.connect(host='mongodb://<baasman>:<Aa20!bbb4>@ds151163.mlab.com:51163/app')
    mongoengine.connect(db='app', username='baasman', password='Aa20!bbb4',
                        host='mongodb://@ds151163.mlab.com:51163/app')
    record = UserRecord(id=432343)
    tag = UserTag(id=432343, tag='sensual')
    boudey = User(email='boudeyz3@gmail.com',
                  user='boudey3',
                  lastfm_username='boudey'
                  )
    boudey.save()
    boudey.add_record(id=432432)

    u = User.get_user('boudey3')

    rec = Record(_id=34242342, artists=['mccoy', 'coltrane'])
    rec.save()
    Record.get_record(id=34242342)

