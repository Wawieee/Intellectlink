from flask_mysql_connector import MySQL
from flask import url_for
mysql = MySQL()



def get_user_photo_url(person_id):
    cursor = mysql.connection.cursor(dictionary=True)
    
    # Fetch the user's photo_url from the database
    photo_url_query = "SELECT photo_url FROM person WHERE person_id = %s"
    cursor.execute(photo_url_query, (person_id,))
    user_data = cursor.fetchone()
    
    cursor.close()
    
    if user_data:
        return user_data['photo_url']
    else:
        # Default placeholder image URL
        return url_for('static', filename='/user_profile/assets/placeholder.png')