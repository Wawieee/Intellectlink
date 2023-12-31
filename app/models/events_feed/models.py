from flask_mysql_connector import MySQL

mysql = MySQL()

def get_upcoming_activities():
    cursor = mysql.connection.cursor(dictionary=True)

    # Query to get upcoming activities
    query = """
    SELECT conference_id, title, location, organizer, position,
    email, deadline, start_date, end_date
    FROM conferences 
    """

    cursor.execute(query)
    upcoming_activities = cursor.fetchall()

    cursor.close()
    return upcoming_activities