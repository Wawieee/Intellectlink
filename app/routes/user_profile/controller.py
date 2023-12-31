from flask import render_template, Blueprint, request, send_file,  jsonify, redirect, url_for, flash, session
import io
from app.models.master_layout.models import *
from app.models.user_profile.models import *
from app.models.search.models import *
from app.models.signup.signup import *
import cloudinary
from cloudinary.uploader import upload as cloudinary_upload
from cloudinary.utils import cloudinary_url
from flask_wtf.csrf import generate_csrf
from math import ceil
from flask import current_app as app


user_profile_blueprint = Blueprint('user_profile_blueprint', __name__, template_folder='templates')

@user_profile_blueprint.route('/user_profile/<int:person_id>')
def user_profile(person_id):
    user_details = get_user_details(person_id)
    # Print session information for debugging
    app.logger.info(f"Session in user_profile route: {session}")
    return render_template('user_profile/user_profile.html', user_details=user_details, person_id=person_id)

@user_profile_blueprint.route('/user_researches/<int:person_id>', methods=['GET'])
def user_researches(person_id):  
    paper_type = request.args.get('type', 'All')
    privacy = request.args.get('privacy', 'All')

    if paper_type not in ['All', 'Research', 'Journals']:
        paper_type = 'All'

    if privacy not in ['All', 'Public', 'Private']:
        privacy = 'All'

    page = int(request.args.get('page', 1))
    papers_per_page = 4  # Adjust the number of papers per page as needed

    user_papers = get_filtered_papers(person_id, paper_type, privacy)
    total_papers = len(user_papers)
    total_pages = ceil(total_papers / papers_per_page)

    start_index = (page - 1) * papers_per_page
    end_index = start_index + papers_per_page
    paginated_papers = user_papers[start_index:end_index]

    user_details = get_user_details(person_id)
    
    return render_template(
        'user_profile/user_researches.html',
        user_papers=paginated_papers,
        user_details=user_details,
        person_id=person_id,
        total_pages=total_pages,
        current_page=page,
        selected_type=paper_type,  # Pass the selected type for highlighting in the template
        selected_privacy=privacy  # Pass the selected privacy for highlighting in the template
    )
    
@user_profile_blueprint.route('/user_profile/<int:person_id>/view_file/<int:paper_id>')
def view_file(person_id, paper_id):
    increment_click_count(paper_id)
    paper_data = get_paper_details(person_id, paper_id)
    user_details = get_user_details(person_id)

    return render_template('user_profile/view_file.html', person_id=person_id, paper_id=paper_id, paper_data=paper_data, user_details=user_details)
 

    

@user_profile_blueprint.route('/other_profile/<int:other_person_id>')
def other_profile(other_person_id):
#    if 'person_id' in session and session['person_id'] == other_person_id:
#        # If the user is viewing their own profile, redirect to user_profile route
#        user_details = get_user_details(other_person_id)
#        return redirect(url_for('user_profile_blueprint.user_profile', user_details=user_details, person_id=other_person_id))
    
    session_id = session.get('person_id')
    print(f"Session ID: {session_id}")
    # Get other user details for non-current user
    other_user_details = get_other_user_details(other_person_id)
    return render_template('user_profile/other_profile.html', other_person_id=other_person_id, other_user_details=other_user_details)

@user_profile_blueprint.route('/other_researches/<int:other_person_id>', methods=['GET'])
def other_researches(other_person_id):  
    paper_type = request.args.get('type', 'All')
    privacy = request.args.get('privacy', 'All')

    if paper_type not in ['All', 'Research', 'Journals']:
        paper_type = 'All'

    if privacy not in ['All', 'Public', 'Private']:
        privacy = 'All'


    page = int(request.args.get('page', 1))
    papers_per_page = 4  # Adjust the number of papers per page as needed

    other_user_papers = get_other_filtered_papers(other_person_id, paper_type, privacy)
    total_papers = len(other_user_papers)
    total_pages = ceil(total_papers / papers_per_page)

    start_index = (page - 1) * papers_per_page
    end_index = start_index + papers_per_page
    paginated_papers = other_user_papers[start_index:end_index]

    other_user_details = get_other_user_details(other_person_id)
    
    return render_template(
        'user_profile/other_researches.html',
        other_user_papers=paginated_papers,
        other_user_details=other_user_details,
        other_person_id=other_person_id,
        total_pages=total_pages,
        current_page=page,
        selected_type=paper_type,  # Pass the selected type for highlighting in the template
        selected_privacy=privacy  # Pass the selected privacy for highlighting in the template
    )
    
@user_profile_blueprint.route('/other_profile/<int:other_person_id>/other_viewfile/<int:paper_id>')
def other_view_file(other_person_id, paper_id):
    increment_click_count(paper_id)
    paper_data = get_other_paper_details(other_person_id, paper_id)

    # Check if the current user is one of the authors
    current_user_id = session.get('person_id')
    is_author = str(current_user_id) in paper_data.get('authors_info', '')

    if is_author:
        return redirect(url_for('user_profile_blueprint.view_file', person_id=current_user_id, paper_id=paper_id))
    else:
        return render_template('user_profile/other_viewfile.html', other_person_id=other_person_id, paper_id=paper_id, paper_data=paper_data)

 


@user_profile_blueprint.route('/user_profile/<int:person_id>/download_paper/<int:paper_id>')
def download_paper(person_id, paper_id):
    paper_data = get_paper_details(person_id, paper_id)

    # Ensure the paper data and PDF file exist
    if paper_data and paper_data.get('pdf_file'):
        # Send the PDF file as a download
        pdf_data = base64.b64decode(paper_data['pdf_file'])
        return send_file(
            io.BytesIO(pdf_data),
            download_name=f"{paper_data['title']}.pdf",
            mimetype='application/pdf',
            as_attachment=True  # Prompt download instead of displaying in the browser
        )
    else:
        # Handle the case where the paper data or PDF file is not found
        return "Paper not found or PDF file is missing", 404

@user_profile_blueprint.route('/user_profile/<int:person_id>/post_paper', methods=['GET', 'POST'])
def post_paper(person_id):
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        paper_type = request.form['paper_type']
        privacy = request.form['privacy']
        pub_date = request.form['pub_date']
        pdf_file = request.files['pdf_file']
        subjects = request.form.getlist('subjects[]')
        co_authors = request.form.getlist('co_authors[]')  # Assuming you have an input field named 'co_authors'

        # Call the model function to insert paper into the database
        insert_paper(person_id, title, abstract, paper_type, privacy, pub_date, pdf_file.read(), subjects, co_authors)

        flash('Paper added successfully!', 'success')
        return redirect(url_for('user_profile_blueprint.user_researches', person_id=person_id))
    
    user_details = get_user_details(person_id)
    subjects = get_all_subjects()
    return render_template('user_profile/post_paper.html', user_details=user_details, person_id=person_id, subjects=subjects)

@user_profile_blueprint.route('/get_author_names/<int:person_id>/<string:entered_name>', methods=['GET'])
def get_author_names(person_id, entered_name):
    cursor = mysql.connection.cursor(dictionary=True)

    # Pagination parameters
    page = request.args.get('page', default=1, type=int)
    results_per_page = 10

    # Calculate the offset based on the page number and results per page
    offset = (page - 1) * results_per_page

    # Fetch a limited number of author names matching the entered name (case-insensitive)
    author_names_query = """
    SELECT person_id, name
    FROM person
    WHERE person_id != %s  -- Exclude the main user
      AND LOWER(name) LIKE %s
    LIMIT %s OFFSET %s
    """
    cursor.execute(author_names_query, (person_id, f"%{entered_name.lower()}%", results_per_page, offset))
    author_names = cursor.fetchall()

    cursor.close()

    return jsonify(author_names)






@user_profile_blueprint.route('/user_profile/<int:person_id>/delete_paper/<int:paper_id>', methods=['GET', 'POST'])
def delete_paper(person_id, paper_id):
    # Add logic to delete the paper and related data
    delete_paper_data(paper_id)

    flash('Paper deleted successfully!', 'success')
    return redirect(url_for('user_profile_blueprint.user_researches', person_id=person_id))

@user_profile_blueprint.route('/user_profile/<int:person_id>/edit_paper/<int:paper_id>', methods=['GET', 'POST'])
def edit_paper(person_id, paper_id):
    user_details = get_user_details(person_id)
    if request.method == 'POST':
        title = request.form['title']
        abstract = request.form['abstract']
        subjects = [int(subject_id) for subject_id in request.form.getlist('subjects')]
        authors = [int(author_id) for author_id in request.form.getlist('authors')]
        privacy = request.form['privacy']
        paper_type = request.form['paper_type']
        pub_date = request.form['pub_date']
        

        # Call the update_paper_data function with individual parameters
        update_paper_data(paper_id, title, abstract, subjects, authors, privacy, paper_type, pub_date, person_id)
        
        flash('Paper updated successfully!', 'success')
        return redirect(url_for('user_profile_blueprint.user_researches', paper_id=paper_id, person_id=person_id))
    else:
        paper_data = get_paper_details(person_id, paper_id)
        subjects = get_all_subjects()
        authors = get_all_authors()
        existing_subjects = get_existing_subjects(paper_id)
        existing_authors = get_existing_authors(paper_id)
        return render_template('user_profile/edit_paper.html',
                               person_id=person_id,
                               paper_id=paper_id,
                               paper_data=paper_data,
                               subjects=subjects,
                               authors=authors,
                               existing_subjects=existing_subjects,
                               existing_authors=existing_authors,
                               user_details=user_details)
        
@user_profile_blueprint.route('/edit_profile/<int:person_id>', methods=['GET', 'POST'])
def edit_profile(person_id):
    if request.method == 'GET':
        # Retrieve user details for pre-filling the form
        user_details = get_user_details(person_id)

        # Fetch the list of subjects from your database
        subjects = get_all_subjects()
        print("All subject:", subjects)

        # Fetch the user's existing interests (subjects)
        user_interests = get_user_interests(person_id)
        print("User Interests:", user_interests)
        
        updated_interests = {'newInterests': 'New interests HTML content'}

        return render_template('user_profile/edit_profile.html', user_details=user_details, person_id=person_id, subjects=subjects, user_interests=user_interests)

    # ... rest of your code
    elif request.method == 'POST':
        # Retrieve user details again for the existing photo_url
        user_details = get_user_details(person_id)

        # Handle form submission to update user details and interests in the database
        name = request.form.get('name')
        email = request.form.get('email')
        gender = request.form.get('gender')
        phone = request.form.get('phone')
        address = request.form.get('address')
        age = request.form.get('age')
        new_interests = request.form.getlist('interests[]')
        print("New Interests:", new_interests)
        new_subject = request.form.get('newSubject')
        if new_subject:
            # Call the function to add the new subject to the database
            add_subject_result = add_subject(new_subject)  # Assuming you have defined the add_subject function
            if 'error' in add_subject_result:
                # If adding the subject failed, handle the error and return a response
                flash(add_subject_result['error'], 'error')
                return redirect(url_for('user_profile_blueprint.edit_profile', person_id=person_id))
        # Check if a new file is uploaded
        if 'photo' in request.files and request.files['photo'].filename:
            photo_file = request.files['photo']

            # Check if the uploaded file is an allowed image type and size
            allowed_extensions = {'jpg', 'jpeg', 'png'}
            max_file_size = 1 * 1024 * 1024  # 1MB

            if (
                photo_file.filename.lower().rsplit('.', 1)[1] in allowed_extensions
                and photo_file.tell() <= max_file_size
            ):
                # Upload the photo to Cloudinary within the 'intellectlink' folder
                upload_result = cloudinary.uploader.upload(photo_file, folder='intellectlink')
                photo_url = upload_result.get('secure_url', '')
            else:
                # Flash an error message if the uploaded file is not valid
                flash('Invalid image file. Accepted image types: JPG, JPEG, PNG. Maximum size: 1MB.', 'error')
                # Redirect back to the edit profile page without updating user details
                return redirect(url_for('user_profile_blueprint.edit_profile', person_id=person_id))
        else:
            # Use the existing photo_url if no new image is uploaded
            photo_url = user_details.get('person_details', {}).get('photo_url', '')

            new_subject = request.form.get('newSubject')
        if new_subject:
            # Call the function to add the new subject to the database
            add_interest(new_subject)  # Assuming you have defined the add_interest function

            subjects = get_all_subjects()
            
        # Update the user details and interests in the database with the valid photo_url
        update_user_details(person_id, name, email, gender, phone, address, age, new_interests, photo_url)

        # Flash a success message
        flash('Profile successfully updated!', 'success')
        session['photo_url'] = photo_url
        # Redirect back to the user profile page after editing
        return redirect(url_for('user_profile_blueprint.user_profile', person_id=person_id))
    
@user_profile_blueprint.route('/add_subject', methods=['POST'])
def add_subject():
    try:
        subjectname = request.form['subjectname']

        # Check if the subjectname already exists
        cursor = mysql.connection.cursor()
        cursor.execute("SELECT subject_id FROM subject WHERE subjectname = %s", (subjectname,))
        existing_subject = cursor.fetchone()
        cursor.close()

        if existing_subject:
            # Subjectname already exists, return an error response
            return jsonify({'error': 'Subject already exists'}), 400

        # Insert the new subject into the database
        cursor = mysql.connection.cursor()
        cursor.execute("INSERT INTO subject (subjectname) VALUES (%s)", (subjectname,))
        mysql.connection.commit()  # Commit the transaction
        new_subject_id = cursor.lastrowid  # Retrieve the ID of the newly inserted subject
        cursor.close()

        # Return the new subject ID as a JSON response
        return jsonify({'subject_id': new_subject_id}), 200
    except Exception as e:
        # Log the exception for debugging
        print(e)
        return jsonify({'error': 'An error occurred while processing your request'}), 500



@user_profile_blueprint.route('/send_request/<int:other_person_id>/<int:paper_id>', methods=['POST'])
def send_request(other_person_id, paper_id):
    if request.method == 'POST':
        sender_person_id = session.get("person_id")  # Assuming you have a session variable
        message = request.form.get('message')

        # Validate and save the request to the database
        if sender_person_id and other_person_id and paper_id and message:
            cursor = mysql.connection.cursor()
            insert_request_query = """
            INSERT INTO request (sender_person_id, receiver_person_id, paper_id, message)
            VALUES (%s, %s, %s, %s)
            """
            cursor.execute(insert_request_query, (sender_person_id, other_person_id, paper_id, message))
            mysql.connection.commit()
            cursor.close()
            flash('Request submitted successfully. You will be notified once it is reviewed.', 'success')
            # Redirect to the same page after submitting the request
            return redirect(url_for('user_profile_blueprint.other_view_file', other_person_id=other_person_id, paper_id=paper_id))
    
    # Handle errors or invalid requests
    return redirect(url_for('user_profile_blueprint.other_view_file', other_person_id=other_person_id, paper_id=paper_id))
    
    

# REQUEST APPROVAL
@user_profile_blueprint.route('/approve_request/<int:request_id>', methods=['POST'])
def approve_request_route(request_id):
    if approve_request_function(request_id):
        flash('Request approved successfully.', 'success')
    else:
        flash('Failed to approve request.', 'error')
    
    # Fetch the updated list of pending requests
    pending_requests = get_pending_requests(session['person_id'])
    
    return render_template('user_profile/request_approval.html', pending_requests=pending_requests)

@user_profile_blueprint.route('/reject_request/<int:request_id>', methods=['POST'])
def reject_request_route(request_id):
    if reject_request_function(request_id):
        flash('Request rejected successfully.', 'success')
    else:
        flash('Failed to reject request.', 'error')
    
    # Fetch the updated list of pending requests
    pending_requests = get_pending_requests(session['person_id'])
    
    return render_template('user_profile/request_approval.html', pending_requests=pending_requests)

# Add this route to display the list of pending requests
@user_profile_blueprint.route('/request_approval/<int:person_id>', methods=['GET'])
def request_approval(person_id):
    # Fetch the list of pending requests
    pending_requests = get_pending_requests(session['person_id'])
    
    return render_template('user_profile/request_approval.html', person_id=person_id, pending_requests=pending_requests)



# NOTIFICATION
@user_profile_blueprint.route('/notifications')
def notifications():
    person_id = session.get('person_id')  # Assuming you store the user's ID in the session
    notifications = get_notifications(person_id)
    return render_template('user_profile/notification.html', notifications=notifications)

