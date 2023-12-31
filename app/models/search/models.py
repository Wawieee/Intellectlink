from flask_mysql_connector import MySQL

mysql = MySQL()

def search_papers(keywords):
    cursor = mysql.connection.cursor(dictionary=True)

    # Assuming 'keywords' is a space-separated list of keywords
    keyword_list = keywords.split()

    # Query to search for papers based on keywords
    query = """
    SELECT DISTINCT p.*
    FROM paper p
    LEFT JOIN paper_subject ps ON p.paper_id = ps.paper_id
    WHERE MATCH(p.title, p.abstract) AGAINST (%s IN BOOLEAN MODE)
        OR p.type IN ({})
        OR ps.subject_id IN ({})
    """.format(', '.join(['%s'] * len(keyword_list)), ', '.join(['%s'] * len(keyword_list)))

    # Duplicate the keyword_list for both type and subject
    params = keyword_list * 2
    cursor.execute(query, params)

    search_results = cursor.fetchall()

    cursor.close()
    return search_results