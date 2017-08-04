from flask import Blueprint

main = Blueprint('main', __name__)

from . import views, errors
from ..models import Permission


# Add access to permissions to all templates
@main.app_context_processor
def inject_permissions():
    return dict(Permission=Permission)
