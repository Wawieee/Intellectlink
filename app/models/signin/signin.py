from flask_mysql_connector import MySQL
from flask import Flask, request, render_template, redirect

mysql = MySQL()




def add_users(name, email, role, gender, phone, address, age, photo_url):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        INSERT INTO person (role, name, email, gender, phone, address, age, photo_url)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """, (role, name, email, gender, phone, address, age, photo_url))
    mysql.connection.commit()
    cursor.close()

def get_user_by_email(email):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user


def get_user_interests(person_id):
    cursor = mysql.connection.cursor()
    cursor.execute("""
        SELECT s.subjectname
        FROM person_subject ps
        JOIN subject s ON ps.subject_id = s.subject_id
        WHERE ps.person_id = %s
    """, (person_id,))
    interests = [row[0] for row in cursor.fetchall()]
    cursor.close()
    return interests