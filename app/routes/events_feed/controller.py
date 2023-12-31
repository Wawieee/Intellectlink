from flask import render_template, Blueprint
from app.models.events_feed.models import get_upcoming_activities

bp_events = Blueprint('bp_events', __name__, static_folder='static')

@bp_events.route("/events_feed/<int:person_id>")
def events_route(person_id):
    # Call the upcoming_activities method from the Events class
    conferences = get_upcoming_activities()

    return render_template('events_feed/events_feed.html', conferences=conferences, person_id=person_id)
