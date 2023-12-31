from flask import Flask, request, render_template, redirect
from app.models.signup.signup import *
from flask import Blueprint, render_template, session, redirect, url_for
from flask import request
from flask import flash
from app.routes.admin.signin.admin_routes import adminroute


signuproute = Blueprint("signuproute", __name__)



@signuproute.route("/interest", methods=["GET", "POST"])
def interest_route():
    if request.method == "POST":
        email = session.get('email')
        user = get_user_by_email(email)
        if user:
            person_id = user.get('person_id')
            interests = request.form.getlist('interests')
            save_interests(person_id, interests)
            session['person_id'] = person_id
            session['photo_url'] = user.get('photo_url', '')  # Update with the correct key from your user data
            session['user_name'] = user.get('name', '')  # Update with the correct key from your user data
            flash("Interests saved successfully!")
            return redirect(url_for('user_profile_blueprint.user_profile', person_id=person_id))
        else:
            flash("User not found. Please log in again.")
            return redirect(url_for('user_profile.user_profile'))
    else:
        subjects = get_subjects()
        
        if not subjects:
            flash("No subjects available.")
            return redirect(url_for("signinroute.base"))
        
        print(subjects)  # Add this line for debugging
        return render_template("signup/interest.html", subjects=subjects)


