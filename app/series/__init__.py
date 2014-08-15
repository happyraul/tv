from flask import Blueprint

series = Blueprint('series', __name__)

from . import views
