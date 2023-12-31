from flask_mysql_connector import MySQL
from app.models.signup.signup import *
from cloudinary.uploader import upload
import base64
from humanize import naturaltime
from datetime import datetime
mysql = MySQL()


# USER_PROFILE
def get_user_details(person_id):
    cursor = mysql.connection.cursor(dictionary=True)

    # Fetch person details
    person_query = "SELECT * FROM person WHERE person_id = %s"
    cursor.execute(person_query, (person_id,))
    person_details = cursor.fetchone()

    # Fetch person subjects (interests)
    interest_query = """
    SELECT s.subjectname
    FROM person_subject ps
    JOIN subject s ON ps.subject_id = s.subject_id
    WHERE ps.person_id = %s
    """
    cursor.execute(interest_query, (person_id,))
    interests = [interest['subjectname'] for interest in cursor.fetchall()]

    # Fetch total click count of all papers
    click_count_query = """
    SELECT SUM(cc.click_count) AS total_click_count
    FROM click_count_table cc
    JOIN paper p ON cc.paper_id = p.paper_id
    WHERE p.personID = %s
    """
    cursor.execute(click_count_query, (person_id,))
    total_click_count = cursor.fetchone()['total_click_count']

    # Fetch at least 3 featured papers
    featured_papers_query = """
    SELECT
        pp.paper_id,
        p.title,
        p.abstract,
        CASE
            WHEN j.paperId IS NOT NULL THEN 'journal'
            WHEN r.paperid IS NOT NULL THEN 'research'
            ELSE 'unknown'
        END AS paper_type,
        CASE
            WHEN pub.paperid IS NOT NULL THEN 'public'
            WHEN priv.paperid IS NOT NULL THEN 'private'
            ELSE 'unknown'
        END AS privacy,
        MAX(COALESCE(j.pub_date, r.pub_date)) AS pub_date,
        GROUP_CONCAT(DISTINCT s.subjectname) AS subjects,
        COALESCE(SUM(DISTINCT cc.click_count), 0) AS `reads`,
        GROUP_CONCAT(DISTINCT CONCAT(pers.photo_url, '|', COALESCE(pp.person_id, p.personID), '|', COALESCE(pers.name, a.name))) AS authors_info
    FROM paper_person pp
    JOIN paper p ON pp.paper_id = p.paper_id
    LEFT JOIN paper_subject ps ON p.paper_id = ps.paper_id
    LEFT JOIN click_count_table cc ON p.paper_id = cc.paper_id
    LEFT JOIN journal j ON p.paper_id = j.paperId
    LEFT JOIN research r ON p.paper_id = r.paperid
    LEFT JOIN public pub ON p.paper_id = pub.paperid
    LEFT JOIN private priv ON p.paper_id = priv.paperid
    LEFT JOIN subject s ON ps.subject_id = s.subject_id
    LEFT JOIN person_subject psub ON pp.person_id = psub.person_id  -- Adjust the join condition
    LEFT JOIN subject s2 ON psub.subject_id = s2.subject_id
    LEFT JOIN person a ON pp.person_id = a.person_id  -- Adjust the join condition
    LEFT JOIN person pers ON pp.person_id = pers.person_id  -- Adjust the join condition
    WHERE pp.person_id = %s  -- Adjust the condition to filter by person_id in paper_person table
    GROUP BY p.paper_id, p.title, p.abstract, paper_type, privacy
    ORDER BY `reads` DESC  -- Order by click count in descending order
    LIMIT 3
    """
    cursor.execute(featured_papers_query, (person_id,))
    featured_papers = cursor.fetchall()
    
    cursor.close()

    # Include authors_info in the returned dictionary
    return {
        "person_details": person_details,
        "interests": interests,
        "total_click_count": total_click_count,
        "featured_papers": [
            {
                **paper,
                "authors_info": get_paper_authors_info(paper['paper_id'])
            }
            for paper in featured_papers
        ]
    }

# USER_PROFILE
def get_paper_authors_info(paper_id):
    cursor = mysql.connection.cursor(dictionary=True)
    
    # Fetch authors' information for a given paper_id
    authors_info_query = """
    SELECT DISTINCT
        psub.person_id,
        a.name,
        a.photo_url,
        a.email
    FROM paper_person psub
    JOIN person a ON psub.person_id = a.person_id
    WHERE psub.paper_id = %s
    """
    cursor.execute(authors_info_query, (paper_id,))
    authors_info = cursor.fetchall()

    cursor.close()

    # Concatenate authors' information into a string
    authors_info_str = ",".join(
        f"{author['photo_url']}|{author['person_id']}|{author['name']}|{author['email']}"
        for author in authors_info
    )

    return authors_info_str

# USER_PROFILE
def get_filtered_papers(person_id, paper_type='All', privacy='All'):
    cursor = mysql.connection.cursor(dictionary=True)

    # Fetch filtered papers
    filtered_papers_query = """
    SELECT
        pp.paper_id,
        p.title,
        p.abstract,
        CASE
            WHEN j.paperId IS NOT NULL THEN 'journal'
            WHEN r.paperid IS NOT NULL THEN 'research'
            ELSE 'unknown'
        END AS paper_type,
        CASE
            WHEN pub.paperid IS NOT NULL THEN 'public'
            WHEN priv.paperid IS NOT NULL THEN 'private'
            ELSE 'unknown'
        END AS privacy,
        MAX(COALESCE(j.pub_date, r.pub_date)) AS pub_date,
        GROUP_CONCAT(DISTINCT s.subjectname) AS subjects,
        COALESCE(SUM(DISTINCT cc.click_count), 0) AS `reads`,
        GROUP_CONCAT(DISTINCT CONCAT(pers.photo_url, '|', COALESCE(pp.person_id, p.personID), '|', COALESCE(pers.name, a.name))) AS authors_info
    FROM paper_person pp
    JOIN paper p ON pp.paper_id = p.paper_id
    LEFT JOIN paper_subject ps ON p.paper_id = ps.paper_id
    LEFT JOIN click_count_table cc ON p.paper_id = cc.paper_id
    LEFT JOIN journal j ON p.paper_id = j.paperId
    LEFT JOIN research r ON p.paper_id = r.paperid
    LEFT JOIN public pub ON p.paper_id = pub.paperid
    LEFT JOIN private priv ON p.paper_id = priv.paperid
    LEFT JOIN subject s ON ps.subject_id = s.subject_id
    LEFT JOIN person_subject psub ON pp.person_id = psub.person_id
    LEFT JOIN subject s2 ON psub.subject_id = s2.subject_id
    LEFT JOIN person a ON p.personID = a.person_id  -- Join to get author details
    LEFT JOIN person pers ON pp.person_id = pers.person_id
    WHERE pp.person_id = %s
    AND (
        (%s = 'All' AND (j.paperId IS NOT NULL OR r.paperid IS NOT NULL))
        OR (%s = 'Research' AND r.paperid IS NOT NULL)
        OR (%s = 'Journals' AND j.paperId IS NOT NULL)
    )
    AND (
        (%s = 'All' AND (pub.paperid IS NOT NULL OR priv.paperid IS NOT NULL))
        OR (%s = 'Public' AND pub.paperid IS NOT NULL)
        OR (%s = 'Private' AND priv.paperid IS NOT NULL)
    )
    GROUP BY pp.paper_id, p.title, p.abstract, paper_type, privacy
    ORDER BY pub_date DESC  -- Order by pub_date in descending order
    """
    cursor.execute(filtered_papers_query, (person_id, paper_type, paper_type, paper_type, privacy, privacy, privacy))
    filtered_papers = cursor.fetchall()

    cursor.close()

    return [
        {
            **paper,
                "authors_info": get_paper_authors_info(paper['paper_id'])
        }
        for paper in filtered_papers
    ]

# USER_PROFILE
def get_paper_details(person_id, paper_id):
    cursor = mysql.connection.cursor(dictionary=True)

    # Fetch paper details including PDF blob
    paper_details_query = """
    SELECT
        p.paper_id,
        p.title,
        p.abstract,
        p.pdf_file,
        CASE
            WHEN j.paperId IS NOT NULL THEN 'journal'
            WHEN r.paperid IS NOT NULL THEN 'research'
            ELSE 'unknown'
        END AS paper_type,
        CASE
            WHEN pub.paperid IS NOT NULL THEN 'public'
            WHEN priv.paperid IS NOT NULL THEN 'private'
            ELSE 'unknown'
        END AS privacy,
        COALESCE(MAX(j.pub_date), MAX(r.pub_date)) AS pub_date,
        COALESCE(SUM(DISTINCT cc.click_count), 0) AS `reads`,
        GROUP_CONCAT(DISTINCT CONCAT(a.photo_url, '|', a.name, '|', pp.person_id) SEPARATOR ',') AS authors_info
    FROM paper p
    LEFT JOIN journal j ON p.paper_id = j.paperId
    LEFT JOIN click_count_table cc ON p.paper_id = cc.paper_id
    LEFT JOIN research r ON p.paper_id = r.paperid
    LEFT JOIN public pub ON p.paper_id = pub.paperid
    LEFT JOIN private priv ON p.paper_id = priv.paperid
    LEFT JOIN paper_person pp ON p.paper_id = pp.paper_id
    LEFT JOIN person a ON pp.person_id = a.person_id
    WHERE p.paper_id = %s
    GROUP BY p.paper_id, p.title, p.abstract, paper_type, privacy;
    """
    cursor.execute(paper_details_query, (paper_id,))
    paper_details = cursor.fetchone()
        # Convert the pdf_file to base64-encoded string
    if paper_details and 'pdf_file' in paper_details:
        pdf_file_data = paper_details['pdf_file']
        if pdf_file_data:
            pdf_file_base64 = base64.b64encode(pdf_file_data).decode('utf-8')
            paper_details['pdf_file'] = pdf_file_base64
    cursor.close()

    return paper_details






def update_user_details(person_id, name, email, gender, phone, address, age, interests, photo_url):
    try:
        cursor = mysql.connection.cursor()

        # Update the user details in the person table, including the Cloudinary photo URL
        update_query = """
        UPDATE person
        SET name = %s, email = %s, gender = %s, phone = %s, address = %s, age = %s, photo_url = %s
        WHERE person_id = %s
        """
        cursor.execute(update_query, (name, email, gender, phone, address, age, photo_url, person_id))

        # Delete existing interests for the user
        cursor.execute("DELETE FROM person_subject WHERE person_id = %s", (person_id,))

        # Save the new interests for the user
        save_interests(person_id, interests)

        # Commit the changes
        mysql.connection.commit()

    except Exception as e:
        # Handle the exception (log, rollback, etc.)
        print(f"Error updating user details: {e}")
        mysql.connection.rollback()

    finally:
        # Close the cursor
        cursor.close()
        
def get_all_subjects():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM subject")
    subjects = cursor.fetchall()
    cursor.close()
    return subjects

def get_user_interests(person_id):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT subject_id FROM person_subject WHERE person_id = %s", (person_id,))
    user_interests = [row['subject_id'] for row in cursor.fetchall()]
    cursor.close()
    return user_interests







# OTHER_PROFILE
def get_other_user_details(other_person_id):
    cursor = mysql.connection.cursor(dictionary=True)

    # Fetch person details for the other user
    person_query = "SELECT * FROM person WHERE person_id = %s"
    cursor.execute(person_query, (other_person_id,))
    person_details = cursor.fetchone()

    # Fetch other person's subjects (interests)
    interest_query = """
    SELECT s.subjectname
    FROM person_subject ps
    JOIN subject s ON ps.subject_id = s.subject_id
    WHERE ps.person_id = %s
    """
    cursor.execute(interest_query, (other_person_id,))
    interests = [interest['subjectname'] for interest in cursor.fetchall()]

    # Fetch total click count of all papers for the other user
    click_count_query = """
    SELECT SUM(cc.click_count) AS total_click_count
    FROM click_count_table cc
    JOIN paper p ON cc.paper_id = p.paper_id
    WHERE p.personID = %s
    """
    cursor.execute(click_count_query, (other_person_id,))
    total_click_count = cursor.fetchone()['total_click_count']

    # Fetch at least 3 featured papers for the other user
    featured_papers_query = """
    SELECT
        p.paper_id,
        p.title,
        p.abstract,
        CASE
            WHEN j.paperId IS NOT NULL THEN 'journal'
            WHEN r.paperid IS NOT NULL THEN 'research'
            ELSE 'unknown'
        END AS paper_type,
        CASE
            WHEN pub.paperid IS NOT NULL THEN 'public'
            WHEN priv.paperid IS NOT NULL THEN 'private'
            ELSE 'unknown'
        END AS privacy,
        MAX(COALESCE(j.pub_date, r.pub_date)) AS pub_date,
        GROUP_CONCAT(DISTINCT s.subjectname) AS subjects,
        COALESCE(SUM(DISTINCT cc.click_count), 0) AS `reads`,
        GROUP_CONCAT(DISTINCT CONCAT(pers.photo_url, '|', COALESCE(pp.person_id, p.personID), '|', COALESCE(pers.name, a.name))) AS authors_info
    FROM paper_person pp
    JOIN paper p ON pp.paper_id = p.paper_id
    LEFT JOIN paper_subject ps ON p.paper_id = ps.paper_id
    LEFT JOIN click_count_table cc ON p.paper_id = cc.paper_id
    LEFT JOIN journal j ON p.paper_id = j.paperId
    LEFT JOIN research r ON p.paper_id = r.paperid
    LEFT JOIN public pub ON p.paper_id = pub.paperid
    LEFT JOIN private priv ON p.paper_id = priv.paperid
    LEFT JOIN subject s ON ps.subject_id = s.subject_id
    LEFT JOIN person_subject psub ON p.personID = psub.person_id
    LEFT JOIN subject s2 ON psub.subject_id = s2.subject_id
    LEFT JOIN person a ON p.personID = a.person_id  -- Join to get author details
    LEFT JOIN person pers ON pp.person_id = pers.person_id
    WHERE pp.person_id = %s
    GROUP BY p.paper_id, p.title, p.abstract, paper_type, privacy
    ORDER BY `reads` DESC  -- Order by click count in descending order
    LIMIT 3
"""
    cursor.execute(featured_papers_query, (other_person_id,))
    featured_papers = cursor.fetchall()
    
    cursor.close()

    # Include authors_info in the returned dictionary
    return {
        "person_details": person_details,
        "interests": interests,
        "total_click_count": total_click_count,
        "featured_papers": [
            {
                **paper,
                "authors_info": get_paper_authors_info(paper['paper_id'])
            }
            for paper in featured_papers
        ]
    }

# OTHER_PROFILE
def get_other_paper_authors_info(paper_id, other_person_id):
    cursor = mysql.connection.cursor(dictionary=True)
    
    # Fetch authors' information for a given paper_id excluding the other_person_id
    authors_info_query = """
    SELECT DISTINCT
        psub.person_id,
        a.name,
        a.photo_url,
        a.email
    FROM paper_person psub
    JOIN person a ON psub.person_id = a.person_id
    WHERE psub.paper_id = %s
    AND psub.person_id != %s
    """
    cursor.execute(authors_info_query, (paper_id, other_person_id))
    authors_info = cursor.fetchall()

    cursor.close()

    # Concatenate authors' information into a string
    authors_info_str = ",".join(
        f"{author['photo_url']}|{author['person_id']}|{author['name']}|{author['email']}"
        for author in authors_info
    )

    return authors_info_str

# OTHER_PROFILE
def get_other_filtered_papers(other_person_id, paper_type='All', privacy='All'):
    cursor = mysql.connection.cursor(dictionary=True)

    # Fetch filtered papers for the other user
    other_filtered_papers_query = """
    SELECT
        pp.paper_id,
        p.title,
        p.abstract,
        CASE
            WHEN j.paperId IS NOT NULL THEN 'journal'
            WHEN r.paperid IS NOT NULL THEN 'research'
            ELSE 'unknown'
        END AS paper_type,
        CASE
            WHEN pub.paperid IS NOT NULL THEN 'public'
            WHEN priv.paperid IS NOT NULL THEN 'private'
            ELSE 'unknown'
        END AS privacy,
        MAX(COALESCE(j.pub_date, r.pub_date)) AS pub_date,
        GROUP_CONCAT(DISTINCT s.subjectname) AS subjects,
        COALESCE(SUM(DISTINCT cc.click_count), 0) AS `reads`,
        GROUP_CONCAT(DISTINCT CONCAT(pers.photo_url, '|', COALESCE(pp2.person_id, p.personID), '|', COALESCE(pers.name, a.name))) AS authors_info
    FROM paper_person pp
    JOIN paper p ON pp.paper_id = p.paper_id
    LEFT JOIN paper_subject ps ON p.paper_id = ps.paper_id
    LEFT JOIN click_count_table cc ON p.paper_id = cc.paper_id
    LEFT JOIN journal j ON p.paper_id = j.paperId
    LEFT JOIN research r ON p.paper_id = r.paperid
    LEFT JOIN public pub ON p.paper_id = pub.paperid
    LEFT JOIN private priv ON p.paper_id = priv.paperid
    LEFT JOIN subject s ON ps.subject_id = s.subject_id
    LEFT JOIN person_subject psub ON pp.person_id = psub.person_id
    LEFT JOIN subject s2 ON psub.subject_id = s2.subject_id
    LEFT JOIN person a ON p.personID = a.person_id  -- Join to get author details
    LEFT JOIN paper_person pp2 ON p.paper_id = pp2.paper_id
    LEFT JOIN person pers ON pp2.person_id = pers.person_id
    WHERE pp.person_id = %s
    AND (
        (%s = 'All' AND (j.paperId IS NOT NULL OR r.paperid IS NOT NULL))
        OR (%s = 'Research' AND r.paperid IS NOT NULL)
        OR (%s = 'Journals' AND j.paperId IS NOT NULL)
    )
    AND (
        (%s = 'All' AND (pub.paperid IS NOT NULL OR priv.paperid IS NOT NULL))
        OR (%s = 'Public' AND pub.paperid IS NOT NULL)
        OR (%s = 'Private' AND priv.paperid IS NOT NULL)
    )
    GROUP BY pp.paper_id, p.title, p.abstract, paper_type, privacy
    ORDER BY pub_date DESC 
    """
    cursor.execute(other_filtered_papers_query, (other_person_id, paper_type, paper_type, paper_type, privacy, privacy, privacy))
    other_filtered_papers = cursor.fetchall()

    cursor.close()

    return [
        {
            **paper,
            "other_authors_info": get_other_paper_authors_info(paper['paper_id'], other_person_id)
        }
        for paper in other_filtered_papers
    ]

#OTHER PROFILE
def get_other_paper_details(other_person_id, paper_id):
    cursor = mysql.connection.cursor(dictionary=True)

    # Fetch paper details including PDF blob
    paper_details_query = """
    SELECT
        p.paper_id,
        p.title,
        p.abstract,
        p.pdf_file,
        CASE
            WHEN j.paperId IS NOT NULL THEN 'journal'
            WHEN r.paperid IS NOT NULL THEN 'research'
            ELSE 'unknown'
        END AS paper_type,
        CASE
            WHEN pub.paperid IS NOT NULL THEN 'public'
            WHEN priv.paperid IS NOT NULL THEN 'private'
            ELSE 'unknown'
        END AS privacy,
        COALESCE(MAX(j.pub_date), MAX(r.pub_date)) AS pub_date,
        COALESCE(SUM(DISTINCT cc.click_count), 0) AS `reads`,
        GROUP_CONCAT(DISTINCT CONCAT(a.photo_url, '|', a.name, '|', pp.person_id) SEPARATOR ',') AS authors_info
    FROM paper p
    LEFT JOIN journal j ON p.paper_id = j.paperId
    LEFT JOIN click_count_table cc ON p.paper_id = cc.paper_id
    LEFT JOIN research r ON p.paper_id = r.paperid
    LEFT JOIN public pub ON p.paper_id = pub.paperid
    LEFT JOIN private priv ON p.paper_id = priv.paperid
    LEFT JOIN paper_person pp ON p.paper_id = pp.paper_id
    LEFT JOIN person a ON pp.person_id = a.person_id
    WHERE p.paper_id = %s
    GROUP BY p.paper_id, p.title, p.abstract, paper_type, privacy;
    """
    cursor.execute(paper_details_query, (paper_id,))
    paper_details = cursor.fetchone()

    # Convert the pdf_file to base64-encoded string
    if paper_details and 'pdf_file' in paper_details:
        pdf_file_data = paper_details['pdf_file']
        if pdf_file_data:
            pdf_file_base64 = base64.b64encode(pdf_file_data).decode('utf-8')
            paper_details['pdf_file'] = pdf_file_base64

    cursor.close()

    return paper_details

# USER_PROFILE
def increment_click_count(paper_id):
    cursor = mysql.connection.cursor()

    # Check if the paper_id already exists in the click_count_table
    cursor.execute("SELECT paper_id FROM click_count_table WHERE paper_id = %s", (paper_id,))
    result = cursor.fetchone()

    if result:
        # Increment the existing click_count
        cursor.execute("UPDATE click_count_table SET click_count = click_count + 1 WHERE paper_id = %s", (paper_id,))
    else:
        # Insert a new record for the paper_id
        cursor.execute("INSERT INTO click_count_table (paper_id, click_count) VALUES (%s, 1)", (paper_id,))

    # Commit changes to the database
    mysql.connection.commit()
    cursor.close()

def get_pdf_file_data(person_id, paper_id):
    cursor = mysql.connection.cursor()

    # Fetch the PDF file data from the database
    query = """
    SELECT pdf_file
    FROM papers
    WHERE person_id = %s AND paper_id = %s
    """
    cursor.execute(query, (person_id, paper_id))
    result = cursor.fetchone()

    cursor.close()

    if result:
        return result['pdf_file']
    else:
        return None



# models.py
def get_all_co_authors(person_id):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM person WHERE person_id != %s", (person_id,))
    co_authors = cursor.fetchall()
    cursor.close()
    return co_authors

def insert_paper(person_id, title, abstract, paper_type, privacy, pub_date, pdf_file, subjects, co_authors):
    cursor = mysql.connection.cursor()

    # Upload PDF to Cloudinary
    cloudinary_response = upload(pdf_file, folder='pdf_files')
    pdf_url = cloudinary_response['url']

    # Insert paper information
    cursor.execute(
        "INSERT INTO paper (title, abstract, pdf_file, pdf_url, personID) VALUES (%s, %s, %s, %s, %s)",
        (title, abstract, pdf_file, pdf_url, person_id)
    )
    paper_id = cursor.lastrowid

    # Parse existing and new subjects
    existing_subjects = set()
    new_subjects = []
    for subject in subjects:
        if subject.isdigit():
            existing_subjects.add(subject)
        else:
            new_subjects.append(subject.strip())

    # Insert new subjects into the subject table
    for new_subject in new_subjects:
        cursor.execute(
            "INSERT INTO subject (subjectname) VALUES (%s)",
            (new_subject,)
        )
        new_subject_id = cursor.lastrowid
        existing_subjects.add(str(new_subject_id))

    # Insert into paper_subject table
    for subject_id in existing_subjects:
        cursor.execute(
            "INSERT INTO paper_subject (paper_id, subject_id) VALUES (%s, %s)",
            (paper_id, subject_id)
        )

            
    # Insert the main user (person_id) into the paper_person table
    cursor.execute(
        "INSERT INTO paper_person (paper_id, person_id) VALUES (%s, %s)",
        (paper_id, person_id)
    )

    # Insert into paper_person table for other co-authors (if any)
    if co_authors:
        for co_author in co_authors:
            if co_author.isdigit():
                cursor.execute(
                    "INSERT INTO paper_person (paper_id, person_id) VALUES (%s, %s)",
                    (paper_id, co_author)
                )
            else:
                cursor.execute(
                    "INSERT INTO person (name, anonymous) VALUES (%s, 1)",
                    (co_author,)
                )
                new_co_author_id = cursor.lastrowid
                cursor.execute(
                    "INSERT INTO paper_person (paper_id, person_id) VALUES (%s, %s)",
                    (paper_id, new_co_author_id)
                )
            
        
    # Insert into research or journal table based on paper type
    if paper_type == 'Research':
        cursor.execute(
            "INSERT INTO research (personid, paperid, pub_date) VALUES (%s, %s, %s)",
            (person_id, paper_id, pub_date))
    elif paper_type == 'Journal':
        cursor.execute(
            "INSERT INTO journal (personId, paperId, pub_date) VALUES (%s, %s, %s)",
            (person_id, paper_id, pub_date))

    # Insert into public or private table based on privacy
    if privacy == 'Public':
        cursor.execute(
            "INSERT INTO public (personid, paperid) VALUES (%s, %s)",
            (person_id, paper_id))
    elif privacy == 'Private':
        cursor.execute(
            "INSERT INTO private (personid, paperid) VALUES (%s, %s)",
            (person_id, paper_id))
    # Commit changes to the database
    mysql.connection.commit()
    cursor.close()
 
 
def add_interest (subjectname):
    cursor = mysql.connection.cursor()
    cursor.execute("INSERT INTO subject (subjectname) VALUES (%s)", (subjectname))
    mysql.connection.commit()
    cursor.close()
    


def delete_paper_data( paper_id):
    cursor = mysql.connection.cursor()

    # Delete entries from paper_subject table
    cursor.execute("DELETE FROM paper_subject WHERE paper_id = %s", (paper_id,))

    # Delete entries from paper_person table
    cursor.execute("DELETE FROM paper_person WHERE paper_id = %s", (paper_id,))

    # Delete entries from click_count_table table
    cursor.execute("DELETE FROM click_count_table WHERE paper_id = %s", (paper_id,))

    # Delete entries from research or journal table based on paper type
    cursor.execute("DELETE FROM research WHERE paperid = %s", (paper_id,))
    cursor.execute("DELETE FROM journal WHERE paperId = %s", (paper_id,))

    # Delete entries from public or private table based on privacy
    cursor.execute("DELETE FROM public WHERE paperid = %s", (paper_id,))
    cursor.execute("DELETE FROM private WHERE paperid = %s", (paper_id,))

    # Delete the paper entry
    cursor.execute("DELETE FROM paper WHERE paper_id = %s", (paper_id,))

    # Commit changes to the database
    mysql.connection.commit()
    cursor.close()


def update_paper_data(paper_id, title, abstract, subjects, authors, privacy, paper_type, pub_date, main_person_id):
    cursor = mysql.connection.cursor()

    try:
        # Update paper details in the main paper table
        cursor.execute("""
            UPDATE paper
            SET title = %s, abstract = %s
            WHERE paper_id = %s
        """, (title, abstract, paper_id))

        """
        # Insert new subjects for the paper excluding duplicates
        for subject_id in set(subjects):
            try:
                cursor.execute("INSERT INTO paper_subject (paper_id, subject_id) VALUES (%s, %s)", (paper_id, subject_id))
            except mysql.connector.IntegrityError:
                pass  # Skip if subject already exists for the paper

        # Insert new authors for the paper excluding duplicates
        for person_id in set(authors):
            if person_id != main_person_id:
                try:
                    cursor.execute("INSERT INTO paper_person (paper_id, person_id) VALUES (%s, %s)", (paper_id, person_id))
                except mysql.connector.IntegrityError:
                    pass  # Skip if author already exists for the paper
        """

        # Update privacy in the respective table (public or private)
        if privacy == 'Public':
            cursor.execute("""
                INSERT INTO public (personid, paperid)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE personid = VALUES(personid)
            """, (main_person_id, paper_id))
            cursor.execute("DELETE FROM private WHERE paperid = %s", (paper_id,))
        elif privacy == 'Private':
            cursor.execute("""
                INSERT INTO private (personid, paperid)
                VALUES (%s, %s)
                ON DUPLICATE KEY UPDATE personid = VALUES(personid)
            """, (main_person_id, paper_id))
            cursor.execute("DELETE FROM public WHERE paperid = %s", (paper_id,))

        # Update paper type in the respective table (research or journal)
        if paper_type == 'Research':
            cursor.execute("""
                INSERT INTO research (personid, paperid, pub_date)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE pub_date = VALUES(pub_date)
            """, (main_person_id, paper_id, pub_date))
            cursor.execute("DELETE FROM journal WHERE paperId = %s", (paper_id,))
        elif paper_type == 'Journal':
            cursor.execute("""
                INSERT INTO journal (personId, paperId, pub_date)
                VALUES (%s, %s, %s)
                ON DUPLICATE KEY UPDATE pub_date = VALUES(pub_date)
            """, (main_person_id, paper_id, pub_date))
            cursor.execute("DELETE FROM research WHERE paperid = %s", (paper_id,))

        # Commit the changes
        mysql.connection.commit()
    except Exception as e:
        # Rollback in case of any error
        mysql.connection.rollback()
        raise e
    finally:
        cursor.close()

def get_all_authors():
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT * FROM person")
    authors = cursor.fetchall()
    cursor.close()
    return authors

def get_existing_subjects(paper_id):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT subject_id FROM paper_subject WHERE paper_id = %s", (paper_id,))
    existing_subjects = [subject['subject_id'] for subject in cursor.fetchall()]
    cursor.close()
    return existing_subjects

def get_existing_authors(paper_id):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("SELECT person_id FROM paper_person WHERE paper_id = %s", (paper_id,))
    existing_authors = [author['person_id'] for author in cursor.fetchall()]
    cursor.close()
    return existing_authors




def insert_request(sender_id, receiver_id, paper_id):
    try:
        cursor = mysql.connection.cursor()

        # Check if a request from the sender to the receiver for the given paper already exists
        cursor.execute("SELECT * FROM request WHERE sender_id = %s AND receiver_id = %s AND paper_id = %s",
                       (sender_id, receiver_id, paper_id))
        existing_request = cursor.fetchone()

        if not existing_request:
            # Insert the request into the database
            cursor.execute("INSERT INTO request (sender_id, receiver_id, paper_id) VALUES (%s, %s, %s)",
                           (sender_id, receiver_id, paper_id))

            # Commit the changes
            mysql.connection.commit()

            return True  # Request successfully inserted
        else:
            return False  # Request already exists

    except Exception as e:
        # Handle the exception, log the error, etc.
        return False
    finally:
        cursor.close()
        
        
# REQUEST APPROVAL
def get_pending_requests(person_id):
    cursor = mysql.connection.cursor(dictionary=True)
    cursor.execute("""
        SELECT request_id, sender_person_id, request.paper_id, message, created_at, status,
               p.name AS sender_name, pa.title AS paper_title
        FROM request
        JOIN person p ON request.sender_person_id = p.person_id
        JOIN paper pa ON request.paper_id = pa.paper_id
        WHERE receiver_person_id = %s
    """, (person_id,))
    pending_requests = cursor.fetchall()
    cursor.close()

    # Convert created_at to human-readable format
    for request in pending_requests:
        request['created_at'] = naturaltime(datetime.now() - request['created_at'])

    # Sort requests with 'pending' status first, followed by others
    pending_requests.sort(key=lambda x: x['status'] != 'pending')

    return pending_requests

def approve_request_function(request_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE request SET status = 'accepted' WHERE request_id = %s", (request_id,))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error approving request: {str(e)}")
        return False

def reject_request_function(request_id):
    try:
        cursor = mysql.connection.cursor()
        cursor.execute("UPDATE request SET status = 'rejected' WHERE request_id = %s", (request_id,))
        mysql.connection.commit()
        cursor.close()
        return True
    except Exception as e:
        print(f"Error rejecting request: {str(e)}")
        return False
    
    
# Replace this with your function to get notifications from the database


def get_notifications(person_id):
    try:
        cursor = mysql.connection.cursor(dictionary=True)
        cursor.execute(
            "SELECT r.request_id, pa.paper_id, pa.title AS paper_title, pa.personID AS receiver_person_id, r.status, r.updated_at, p.name AS receiver_name " +
            "FROM request r " +
            "JOIN person p ON r.receiver_person_id = p.person_id " +
            "JOIN paper pa ON r.paper_id = pa.paper_id " +
            "WHERE r.sender_person_id = %s " +
            "ORDER BY CASE WHEN r.status IN ('accepted', 'rejected') THEN 0 ELSE 1 END, r.updated_at DESC",
            (person_id,)
        )
        notifications = cursor.fetchall()
        cursor.close()

        # Convert updated_at to human-readable format
        for notification in notifications:
            notification['updated_at'] = naturaltime(datetime.now() - notification['updated_at'])

        return notifications
    except Exception as e:
        print(f"Error fetching notifications: {str(e)}")
        return []