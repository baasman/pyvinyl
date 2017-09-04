from werkzeug.security import generate_password_hash, check_password_hash
import pylast

# TODO: remove this unnecessary class with mongo User model
class FlaskUser():
    def __init__(self, username, email=None,
                 lastfm_user=None, lastfm_password=None):
        self.username = username
        self.email = email
        self.lastfm_user = lastfm_user
        self.lastfm_password = pylast.md5(lastfm_password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    @property
    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        return self.username

    @staticmethod
    def validate_login(password_hash, password):
        return check_password_hash(password_hash, password)
