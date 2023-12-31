from faker import Faker
import mysql.connector
import random
from faker import Faker
import mysql.connector
import random

# Connect to MySQL
connection = mysql.connector.connect(
    host="localhost",
    user="root",
    password="nawawi",
    database="dbintellectlink",
    auth_plugin='mysql_native_password'
)

# Create a Faker instance
fake = Faker()

def insert_paper_person_data(paper_id, person_id, co_authors):
    cursor = connection.cursor()

    try:
        # Check if the paper_id exists in the paper table
        cursor.execute("SELECT COUNT(*) FROM paper WHERE paper_id = %s", (paper_id,))
        if cursor.fetchone()[0] == 0:
            print(f"Paper with ID {paper_id} does not exist.")
            return

        # Check if the person_id exists in the person table
        cursor.execute("SELECT COUNT(*) FROM person WHERE person_id = %s", (person_id,))
        if cursor.fetchone()[0] == 0:
            print(f"Person with ID {person_id} does not exist.")
            return

        # Check if the main author is already associated with the paper
        cursor.execute("""
            SELECT COUNT(*) FROM paper_person WHERE paper_id = %s AND person_id = %s
        """, (paper_id, person_id))
        if cursor.fetchone()[0] > 0:
            print(f"Person with ID {person_id} is already associated with Paper ID {paper_id}.")
            return

        # Insert the main author
        cursor.execute("""
            INSERT INTO paper_person (paper_id, person_id)
            VALUES (%s, %s)
        """, (paper_id, person_id))

        # Insert co-authors
        for co_author_id in co_authors:
            # Check if the co_author_id exists in the person table
            cursor.execute("SELECT COUNT(*) FROM person WHERE person_id = %s", (co_author_id,))
            if cursor.fetchone()[0] == 0:
                print(f"Person with ID {co_author_id} does not exist.")
                continue  # Skip inserting this co-author and proceed to the next one

            # Check if the co-author is already associated with the paper
            cursor.execute("""
                SELECT COUNT(*) FROM paper_person WHERE paper_id = %s AND person_id = %s
            """, (paper_id, co_author_id))
            if cursor.fetchone()[0] > 0:
                print(f"Person with ID {co_author_id} is already associated with Paper ID {paper_id}.")
                continue  # Skip inserting this co-author and proceed to the next one

            # Insert the co-author
            cursor.execute("""
                INSERT INTO paper_person (paper_id, person_id)
                VALUES (%s, %s)
            """, (paper_id, co_author_id))

    except mysql.connector.IntegrityError as e:
        if e.errno == 1062:
            print(f"Duplicate entry for paper_id: {paper_id} and person_id: {person_id}")
        else:
            print(f"An error occurred: {e}")
    finally:
        connection.commit()
        cursor.close()

# ...

# Sample data
for _ in range(10000):  # Insert 5,000 records
    paper_id = random.randint(1, 10000)  # Replace with the actual logic to select a paper_id
    person_id = random.randint(1, 23000)  # Replace with the actual logic to select a person_id
    co_authors = [random.randint(1, 23000) for _ in range(random.randint(1, 5))]  # Example: Generate 1 to 5 co-authors
    insert_paper_person_data(paper_id, person_id, co_authors)

# Close the connection
connection.close()