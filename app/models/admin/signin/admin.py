from flask_mysql_connector import MySQL
from flask import Flask, request, render_template, redirect

mysql = MySQL()

def get_admins():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin")
    admins = cursor.fetchall()
    cursor.close()
    return admins

def get_users():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM person")
    users = cursor.fetchall()
    cursor.close()
    return users

def get_events():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM conferences")
    events = cursor.fetchall()
    cursor.close()
    return events


def check_creds(username, password):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM admin WHERE username = %s AND password = %s", (username, password,))
    admin = cursor.fetchall()
    cursor.close()
    return len(admin)

def add_admin(username, password):
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM admin")
        admins = cursor.fetchall()
        cursor.execute("INSERT INTO admin VALUES (%s, %s, %s)", (len(admins)+1, username, password,))
        mysql.connection.commit()
        cursor.close()
        return "Admin added successfully."
    except Exception as e:
            return f"Failed to add admin: {str(e)}"
    
def delete_admin(id):
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("DELETE FROM admin WHERE adminID = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return "Admin deleted successfully."
    except Exception as e:
        return f"Failed to delete admin: {str(e)}"
    
def edit_admin(id, username, password):
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""UPDATE admin SET username = %s, password = %s WHERE adminID = %s""", (username, password, id,))
        mysql.connection.commit()
        cursor.close()
        return "Admin updated successfully."
    except Exception as e:
        return f"Failed to update admin: {str(e)}"
    
def delete_user(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM person WHERE person_id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return "User deleted successfully."
    except Exception as e:
        return f"Failed to delete user: {str(e)}"
    
def edit_user(id, name, email, phone, address):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("""UPDATE person SET name = %s, email = %s, phone = %s, address = %s WHERE person_id = %s """, (name, email, phone, address, id,))
        mysql.connection.commit()
        cursor.close()
        return "User updated successfully."
    except Exception as e:
        return f"Failed to update user: {str(e)}"
    
def add_event(title, event_desc, loc, org, pos, email, dead, start, end):
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM conferences")
        events = cursor.fetchall()
        cursor.execute("INSERT INTO conferences VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)", (len(events)+1, title, event_desc, loc, org, pos, email, dead, start, end))
        mysql.connection.commit()
        cursor.close()
        return "Event added successfully."
    except Exception as e:
            return f"Failed to add event: {str(e)}"
    
def edit_event(id, title, event_desc, loc, org, pos, email, dead, start, end):
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute("""UPDATE conferences SET title = %s, event_desc = %s, location = %s, organizer = %s, position = %s, email = %s, deadline = %s, start_date = %s, end_date = %s  WHERE conference_id = %s""", (title, event_desc, loc, org, pos, email, dead, start, end, id,))
        mysql.connection.commit()
        cursor.close()
        return "Event updated successfully."
    except Exception as e:
        return f"Failed to update event: {str(e)}"
    

def delete_event(id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("DELETE FROM conferences WHERE conference_id = %s", (id,))
        mysql.connection.commit()
        cursor.close()
        return "Event deleted successfully."
    except Exception as e:
        return f"Failed to delete event: {str(e)}"