from flask import render_template, redirect, request, jsonify, abort, current_app, Response, flash, session, url_for
from . import models as feed
from flask_wtf.csrf import validate_csrf
from flask import Blueprint
from app.models.user_profile.models import *
from app.routes.user_profile.controller import *
import math
research_blueprint = Blueprint('research_blueprint', __name__)
@research_blueprint.route('/research-feed/<int:person_id>', methods=['GET'])
def research_feed(person_id):
    # Check if the user is logged in
    if 'person_id' not in session:
        flash('Please log in to access the research feed.', 'error')
        return redirect(url_for('login'))  # Update with your actual login route

    # Use the search query for both research and journal
    user_details = get_user_details(int(person_id))
    research_data = feed.research.researchfeed()

    # Get the current page number from the query parameters
    page = request.args.get('page', default=1, type=int)

    # Set the number of items per page
    items_per_page = 100

    # Calculate the start and end index for pagination
    start_idx = (page - 1) * items_per_page
    end_idx = start_idx + items_per_page

    # Slice the research_data based on the page
    paginated_research = research_data[start_idx:end_idx]

    total_pages = math.ceil(len(research_data) / items_per_page)

    return render_template('research_feed/feed.html', research=paginated_research, user_details=user_details, person_id=person_id, total_pages=total_pages, current_page=page)


@research_blueprint.route('/update_click_count/<int:paper_id>', methods=['POST'])
def click_count(paper_id):
    if request.method == 'POST':
        try:
            # Verify CSRF token
            csrf_token = request.headers.get('X-CSRFToken')
            if not csrf_token or validate_csrf(csrf_token):
                abort(400, 'Invalid CSRF token')

            data = request.get_json()
            card_id = data.get("click")

            # Update the click count
            count = feed.research.update_click_count(paper_id)

            return jsonify({'success': True, 'count': count, 'token': csrf_token}), 200

        except Exception as e:
            # Use Flask's logging instead of print
            current_app.logger.error(f"An error occurred: {e}")
            return jsonify({'success': False, 'error': str(e)}), 500

@research_blueprint.route('/fetch_file/<int:other_person_id>/view_file/<int:paper_id>', methods=['POST'])
def feed_other_view_file(other_person_id, paper_id):
    # Check if the user is logged in
    if 'person_id' not in session:
        flash('Please log in to view the file.', 'error')
        return redirect(url_for('/'))  # Assuming you have a login route


    paper_data = get_other_paper_details(other_person_id, paper_id)
    other = other_researches(other_person_id)
    request= send_request(other_person_id, paper_id)

    return render_template('research_feed/feed_viewfile.html', other_person_id=other_person_id, paper_id=paper_id,paper_data=paper_data, other=other,request=request)
