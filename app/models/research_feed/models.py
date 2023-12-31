from app import mysql,request,jsonify

class research(object):
    def __init__(self,person_id=None,paper_id=None,pub_date=None, email=None,title=None,abstract=None):
        self.person_id=person_id
        self.paper_id=paper_id
        self.pub_date=pub_date
        self.email=email
        self.title=title
        self.abstract=abstract
 
    @classmethod
    def researchfeed(cls):  # Add cls parameter

        cursor = mysql.connection.cursor(dictionary=True)
        
       

        research_query = f"SELECT title,abstract,pub_date,fname,lname,GROUP_CONCAT(subjectname) AS subjects \
                            FROM (SELECT paper.title,paper.abstract,COALESCE(research.pub_date, journal.pub_date) AS pub_date,person.fname,person.lname,subject.subjectname \
                                FROM paper LEFT JOIN research ON paper.paper_id = research.paperid \
                                    LEFT JOIN journal ON paper.paper_id = journal.paperId \
                                        LEFT JOIN person ON paper.personID = person.person_id \
                                            LEFT JOIN paper_subject ON paper.paper_id = paper_subject.paper_id \
                                                LEFT JOIN subject ON paper_subject.subject_id = subject.subject_id) AS subquery \
                                                    GROUP BY title, abstract, pub_date, fname, lname;"

        cursor.execute(research_query)
        result = cursor.fetchall()
        cursor.close()
        cursor.close()
    
        # Return the result
        return result
    
