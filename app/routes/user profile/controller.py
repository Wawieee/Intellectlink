from flask import render_template, redirect, request, jsonify
from . import models as models
from flask import Blueprint
from app.models import User 

bp_blueprint = Blueprint('bp_blueprint', __name__)


@bp_blueprint.route('/')
def user_profile():

    user_profiles =User.all() 

    return render_template('user_profile.html', data=user_profiles)