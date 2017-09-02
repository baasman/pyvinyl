from app.models import User
from app import login_manager

from app.user_management import FlaskUser


@login_manager.user_loader
def load_user(user):
    user = User.objects.get(user=user)
    if user:
        return FlaskUser(username=user['user'])
    else:
        return None