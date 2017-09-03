from app.models import User
from flask_login import LoginManager

from mongoengine.errors import DoesNotExist

def setup_login_manager():

    login_manager = LoginManager()
    login_manager.login_message = 'You must be logged in to view this page'
    login_manager.login_view = 'auth.login'

    @login_manager.user_loader
    def load_user(user):
        try:
            user = User.objects.get(user=user)
            return user
        except DoesNotExist:
            return None

    return login_manager