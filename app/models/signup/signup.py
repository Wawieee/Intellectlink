from flask_mysql_connector import MySQL

mysql = MySQL()


def get_subjects():
    cursor = mysql.connection.cursor(dictionary=True)
    query = "SELECT subject_id, subjectname FROM subject"
    cursor.execute(query)
    subjects = cursor.fetchall()
    cursor.close()
    return subjects

def save_interests(person_id, interests):
    cursor = mysql.connection.cursor()
    for subject_id in interests:
        cursor.execute("""
            INSERT INTO person_subject (person_id, subject_id)
            VALUES (%s, %s)
        """, (person_id, subject_id))
    mysql.connection.commit()
    cursor.close()


def get_user_by_email(email):
    cursor = mysql.connection.cursor(dictionary=True)  # Use dictionary cursor
    cursor.execute("SELECT * FROM person WHERE email = %s", (email,))
    user = cursor.fetchone()
    cursor.close()
    return user





