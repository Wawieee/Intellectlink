from flask import Blueprint, render_template, session, redirect, url_for
from app import oauth
from authlib.integrations.flask_client import OAuthError
from app.models.signin.signin import *
from app.routes.admin.signin.admin_routes import adminroute
from flask import *



'''pls use "localhost:5000" when signing in kay arte ang google'''

signinroute = Blueprint("signinroute", __name__)

google = oauth.create_client("google")

@signinroute.route('/')
def base():
    return render_template("signin/signin.html")

@signinroute.route("/signin")
def signin():
    return redirect(url_for("signinroute.authorize"))

@signinroute.route("/authorize")
def authorize():
    redirect_uri = url_for('signinroute.callback', _external=True)  # Corrected the route name
    return google.authorize_redirect(redirect_uri)

@signinroute.route("/callback")
def callback():
    try:
        token = google.authorize_access_token()
        resp = google.get('userinfo')
        resp.raise_for_status()
        user_info = resp.json()
        session['email'] = user_info.get('email', None)
        
        existing_user = get_user_by_email(session['email'])

        if existing_user:
            person_id = existing_user.get('person_id')
            # Set person_id in session
            session['photo_url'] = existing_user.get('photo_url', '')
            session['user_name'] = user_info.get('name', '') 
            session['person_id'] = person_id
            return redirect(url_for("user_profile_blueprint.user_profile", person_id=person_id))
        else:
            profile_pic_url = user_info.get('picture', '')
            add_users(
                name=user_info.get('name', ''),
                email=session['email'],
                role='',
                gender=user_info.get('gender', ''),
                phone='',
                address='',
                age=None,
                photo_url=profile_pic_url
            )
            # Get the person_id of the newly added user
            new_user = get_user_by_email(session['email'])
            person_id = new_user.get('person_id')

            # Set person_id in session
            session['person_id'] = person_id
            
            return redirect(url_for("signuproute.interest_route"))

    except OAuthError as e:
        return f"OAuthException: {str(e)}"
    except Exception as e:
        return f"An error occurred: {str(e)}"



@signinroute.route('/auth')
def auth():
    token = google.authorize_access_token()
    user = google.parse_id_token(token)
    # Now you can use the user data as needed
    return 'Welcome, {}'.format(user['name'])



@signinroute.route("/logout")
def logout():
    session.clear()  # Changed the loop and pop to session.clear()
    return redirect('/')
