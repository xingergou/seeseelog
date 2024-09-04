from flask import Blueprint, request
from flask import render_template
views = Blueprint('views', __name__)

@views.route('/servers')
def servers():
    return render_template('/test/servers.html')