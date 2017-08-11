from flask import Blueprint

collection = Blueprint('collection', __name__)

from . import views