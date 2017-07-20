from werkzeug.security import generate_password_hash, check_password_hash


class User():
    def __init__(self, username, email=None,
                 discogs_user=None):
        self.username = username
        self.email = email
        self.discogs_user = discogs_user

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
