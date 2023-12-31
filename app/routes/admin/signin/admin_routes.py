from app import mysql
from flask import Blueprint, render_template, session, redirect, url_for, request, flash, jsonify
from app.models.admin.signin.admin import *

adminroute = Blueprint("adminroute", __name__)

@adminroute.route('/admin_signin', methods=["GET", "POST"])
def admin_signin():
    return render_template("admin/signin/admin_signin.html")

@adminroute.route('/admin', methods=["GET", "POST"])
def admin_feed():
    admins = get_admins()
    users = get_users()
    conferences = get_events()
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        admin = check_creds(username, password)
        if admin == 1:
            return render_template("admin/feed/admin_feed.html", users=users, admins = admins, conferences = conferences)
        else:
            return render_template("admin/signin/admin_signin.html", notif="No existing admin with those credentials.")
    else:
        return render_template("admin/signin/admin_signin.html", notif = "Bad credentials.")

@adminroute.route('/admin_add', methods=["POST"])
def create_admin():
        username = request.form['admin_user']
        password = request.form['admin_pass']
        confirm = request.form['admin_confirm']

        if password == confirm:
            result = add_admin(username, password)
        else:
            result = "Please make sure you confirm your password properly."

        if result == "Admin added successfully.":
            flash(f'Admin: {username} added successfully', 'success')
            return jsonify({'success': True, 'message': 'Admin added successfully'})
        else:
            flash(f"Failed to add admin: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to add admin: {result}"})
        
@adminroute.route('/admin_delete', methods=["POST"])
def remove_admin():
    try:
        id = request.form['delete_admin_id']

        result = delete_admin(id)

        if result == "Admin deleted successfully.":
            flash(f'Admin deleted successfully', 'success')
            return jsonify({'success': True, 'message': 'Admin deleted successfully'})
        else:
            flash(f"Failed to delete admin: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to delete admin: {result}"})
    except Exception as e:
        flash(f"Failed to delete admin: {str(e)}", 'error')
        return jsonify({'success': False, 'error': f"Failed to delete admin: {str(e)}"}), 500
    
@adminroute.route('/admin_edit', methods=["POST"])
def update_admin():
    try:
        id = request.form['edit_admin_id']
        username = request.form['edit_admin_user']
        password = request.form['edit_admin_pass']
        confirm = request.form['edit_admin_confirm']

        if password == confirm:
            result = edit_admin(id, username, password)
        else:
            result = "Please make sure you confirm your password properly."
        
        if result == "Admin updated successfully.":
            flash(f'Admin updated successfully', 'success')
            return jsonify({'success': True, 'message': 'Admin updated successfully'})
        else:
            flash(f"Failed to update admin: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to update admin: {result}"})
    except Exception as e:
        flash(f"Failed to update admin: {str(e)}", 'error')
        return jsonify({'success': False, 'error': f"Failed to update admin: {str(e)}"}), 500


@adminroute.route('/admin/user_delete', methods=["POST"])
def remove_user():
    try:
        id = request.form['delete_user_id']

        result = delete_user(id)

        if result == "User deleted successfully.":
            flash(f'User deleted successfully', 'success')
            return jsonify({'success': True, 'message': 'User deleted successfully'})
        else:
            flash(f"Failed to delete user: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to delete user: {result}"})
    except Exception as e:
        flash(f"Failed to delete user: {str(e)}", 'error')
        return jsonify({'success': False, 'error': f"Failed to delete user: {str(e)}"}), 500
    
@adminroute.route('/admin/user_edit', methods=["POST"])
def update_user():
    try:
        id = request.form['edit_user_id']
        name = request.form['edit_user_name']
        email = request.form['edit_user_email']
        phone = request.form['edit_user_phone']
        address = request.form['edit_user_address']

        result = edit_user(id, name, email, phone, address)

        if result == "User updated successfully.":
            flash(f'User updated successfully', 'success')
            return jsonify({'success': True, 'message': 'User updated successfully'})
        else:
            flash(f"Failed to update user: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to update user: {result}"})
    except Exception as e:
        flash(f"Failed to update user: {str(e)}", 'error')
        return jsonify({'success': False, 'error': f"Failed to update user: {str(e)}"}), 500
    

@adminroute.route('/event_add', methods=["POST"])
def create_event():
        title = request.form['event_title']
        event_desc = request.form['event_desc']
        loc = request.form['event_loc']
        org = request.form['event_org']
        pos = request.form['event_pos']
        email = request.form['event_email']
        dead = request.form['event_dead']
        start = request.form['event_start']
        end = request.form['event_end']

        result = add_event(title, event_desc, loc, org, pos, email, dead, start, end)

        if result == "Event added successfully.":
            flash(f'Event: {title} added successfully', 'success')
            return jsonify({'success': True, 'message': 'Event added successfully'})
        else:
            flash(f"Failed to add event: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to add event: {result}"})
        
@adminroute.route('/event_edit', methods=["POST"])
def update_event():
        event_id = request.form['edit_event_id']
        title = request.form['edit_event_title']
        event_desc = request.form['edit_event_desc']
        loc = request.form['edit_event_loc']
        org = request.form['edit_event_org']
        pos = request.form['edit_event_pos']
        email = request.form['edit_event_email']
        dead = request.form['edit_event_dead']
        start = request.form['edit_event_start']
        end = request.form['edit_event_end']

        result = edit_event(event_id, title, event_desc, loc, org, pos, email, dead, start, end)

        if result == "Event updated successfully.":
            flash(f'Event: {title} updated successfully', 'success')
            return jsonify({'success': True, 'message': 'Event updated successfully'})
        else:
            flash(f"Failed to update event: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to update event: {result}"})
        
@adminroute.route('/event_delete', methods=["POST"])
def remove_event():
        event_id = request.form['delete_event_id']

        result = delete_event(event_id)

        if result == "Event deleted successfully.":
            flash(f'Event deleted successfully', 'success')
            return jsonify({'success': True, 'message': 'Event deleted successfully'})
        else:
            flash(f"Failed to delete event: {result}", 'error')
            return jsonify({'success': False, 'error': f"Failed to delete event: {result}"})