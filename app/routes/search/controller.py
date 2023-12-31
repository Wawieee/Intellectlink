from flask import request, redirect, url_for, render_template
from app.models.search.models import *
from flask import Blueprint

search_blueprint = Blueprint('search_blueprint', __name__, template_folder='templates')

# Route to handle the search
@search_blueprint.route('/search', methods=['GET'])
def search():
    # Get the search term from the query parameters
    search_term = request.args.get('search_term', '')

    # Initialize empty result lists
    paper_results = []
    person_results = []

    # Perform search for papers
    if search_term:
        paper_results = search_papers(search_term)

    # Render the search results page
    return render_template('search/search.html', paper_results=paper_results, person_results=person_results)