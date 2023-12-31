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

# Function to check if a person_id exists
def person_id_exists(person_id, cursor):
    cursor.execute("SELECT COUNT(*) FROM person WHERE person_id = %s", (person_id,))
    result = cursor.fetchone()[0]
    return result == 1

# Function to insert data into the paper table
def insert_paper_data(pdf_file_path, pdf_url, person_id):
    cursor = connection.cursor()

    # Generate random title and abstract
    title = fake.sentence()
    abstract = "\n\n".join(fake.paragraphs())

    # Check if person_id exists
    if not person_id_exists(person_id, cursor):
        print(f"Person with ID {person_id} does not exist.")
        return

    with open(pdf_file_path, 'rb') as file:
        pdf_content = file.read()
        cursor.execute("""
            INSERT INTO paper (title, abstract, pdf_file, pdf_url, personID)
            VALUES (%s, %s, %s, %s, %s)
        """, (title, abstract, pdf_content, pdf_url, person_id))
        paper_id = cursor.lastrowid  # Get the last inserted paper_id

        # Insert into paper_person
        cursor.execute("""
            INSERT INTO paper_person (paper_id, person_id)
            VALUES (%s, %s)
        """, (paper_id, person_id))

        # Insert into paper_subject (assuming a random subject_id)
        subject_ids = [random.choice([1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 20, 21, 22, 45, 46, 47, 48, 49, 50]) for _ in range(random.randint(1, 3))]  # Randomly select 1 to 3 subject_ids
        for subject_id in subject_ids:
            # Check if the combination of paper_id and subject_id already exists
            cursor.execute("SELECT COUNT(*) FROM paper_subject WHERE paper_id = %s AND subject_id = %s", (paper_id, subject_id))
            result = cursor.fetchone()[0]
            if result == 0:  # If the combination doesn't exist, insert it
                cursor.execute("""
                    INSERT INTO paper_subject (paper_id, subject_id)
                    VALUES (%s, %s)
                """, (paper_id, subject_id))
            else:
                print(f"Combination of paper_id {paper_id} and subject_id {subject_id} already exists.")

        # Insert into public or private table (assuming a random choice)
        is_public = random.choice([True, False])
        if is_public:
            cursor.execute("""
                INSERT INTO public (personid, paperid)
                VALUES (%s, %s)
            """, (person_id, paper_id))
        else:
            cursor.execute("""
                INSERT INTO private (personid, paperid)
                VALUES (%s, %s)
            """, (person_id, paper_id))

        # Insert into journal or research table (assuming a random choice)
        is_journal = random.choice([True, False])
        if is_journal:
            cursor.execute("""
                INSERT INTO journal (personId, paperId, pub_date)
                VALUES (%s, %s, %s)
            """, (person_id, paper_id, fake.date_this_decade()))
        else:
            cursor.execute("""
                INSERT INTO research (personid, paperid, pub_date)
                VALUES (%s, %s, %s)
            """, (person_id, paper_id, fake.date_this_decade()))

    connection.commit()

# ...

# Populate the paper table with sample data
for _ in range(10000):  # Insert 10,000 records
    pdf_file_path = random.choice([
        r'C:\Users\NAWAWI\Documents\Wawa Files\pdf_test_file.pdf',
        r'C:\Users\NAWAWI\Documents\Wawa Files\pdf_test_file2.pdf'
    ])  # Choose a random PDF file path
    pdf_url = 'https://res.cloudinary.com/dgsf02uow/image/upload/v1703443636/pdf_files/nlbr6ypbtealgzdrrqgc.pdf'  # Replace with the actual PDF URL
    person_id = random.randint(1, 23000)  # Replace with the actual logic to select a person_id
    insert_paper_data(pdf_file_path, pdf_url, person_id)

# Close the connection
connection.close()