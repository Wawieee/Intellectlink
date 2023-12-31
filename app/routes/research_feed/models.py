from app import mysql
from flask import current_app

class research(object):
    def __init__(self,person_id=None,paper_id=None,pub_date=None, email=None,title=None,abstract=None,page=None):
        self.person_id=person_id
        self.paper_id=paper_id
        self.pub_date=pub_date
        self.email=email
        self.title=title
        self.abstract=abstract
        self.page=page
      
    @classmethod
    def researchfeed(cls):  # Add cls parameter

        cursor = mysql.connection.cursor(dictionary=True)

        research = """
            SELECT 
                paper.title,
                paper.abstract,
                COALESCE(research.pub_date, journal.pub_date) AS pub_date,
                GROUP_CONCAT(DISTINCT person.name) AS authors,
                GROUP_CONCAT(DISTINCT subject.subjectname) AS subjects,
                paper.paper_id,
                click_count_table.click_count,
                private.paperid AS private, 
                public.paperid AS public,
                person.person_id  # Include person_id if needed
            FROM 
                paper 
                LEFT JOIN research ON paper.paper_id = research.paperid 
                LEFT JOIN journal ON paper.paper_id = journal.paperId 
                LEFT JOIN paper_subject ON paper.paper_id = paper_subject.paper_id 
                LEFT JOIN subject ON paper_subject.subject_id = subject.subject_id 
                LEFT JOIN private ON paper.paper_id = private.paperid 
                LEFT JOIN public ON paper.paper_id = public.paperid 
                LEFT JOIN click_count_table ON click_count_table.paper_id = paper.paper_id
                LEFT JOIN paper_person ON paper.paper_id = paper_person.paper_id
                LEFT JOIN person ON paper_person.person_id = person.person_id
            GROUP BY 
                paper.title,
                paper.abstract,
                pub_date,
                paper.paper_id,
                private.paperid,
                public.paperid,
                click_count_table.click_count,
                person.person_id  # Include person_id if needed
            ORDER BY click_count DESC;
        """
                                                                                

        cursor.execute(research)
        result = cursor.fetchall()
        cursor.close()
        cursor.close()

        # Return the result
        return result
        

        """ research_query = f"SELECT title,abstract,pub_date,name,GROUP_CONCAT(subjectname) AS subjects,paper_id,click_count,private,public\
                    FROM (SELECT paper.title,paper.abstract,COALESCE(research.pub_date, journal.pub_date) AS pub_date,person.name,subject.subjectname, \
                        paper.paper_id,click_count_table.click_count,private.paperid AS private, public.paperid AS public  \
                            FROM paper LEFT JOIN research ON paper.paper_id = research.paperid \
                                LEFT JOIN journal ON paper.paper_id = journal.paperId \
                                    LEFT JOIN person ON paper.personID = person.person_id \
                                        LEFT JOIN paper_subject ON paper.paper_id = paper_subject.paper_id \
                                            LEFT JOIN subject ON paper_subject.subject_id = subject.subject_id \
                                                LEFT JOIN private ON paper.paper_id=private.paperid \
                                                    LEFT JOIN public ON paper.paper_id=public.paperid \
                                                        LEFT JOIN click_count_table ON click_count_table.paper_id= paper.paper_id) AS subquery \
                                                            GROUP BY title, abstract, pub_date, name, subquery.paper_id,private,public ORDER BY click_count DESC;" """

       


#class ClickCount(): 
    @classmethod
    def update_click_count(cls, paper_id):
        try:
            with mysql.connection.cursor(dictionary =True) as cursor:
                # Update or create a record in the database
                cursor.execute('SELECT * FROM click_count_table WHERE paper_id = %s', (paper_id,))
                click_count = cursor.fetchone()

                if click_count:
                    cursor.execute('UPDATE click_count_table SET click_count = click_count + 1 WHERE paper_id = %s', (paper_id,))
                else:
                    cursor.execute('INSERT INTO click_count_table (paper_id, click_count) VALUES (%s, 1)', (paper_id,))

                mysql.connection.commit()
                return {'success': True}

        except Exception as e:
            print(f"An error occurred: {e}")
            return {'success': False, 'error': str(e)}
