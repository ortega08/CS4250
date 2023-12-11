#-------------------------------------------------------------------------
# AUTHOR: Jessica Ortega
# FILENAME: db_connection_solution.py
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
# --> add your Python code here
import psycopg2

def connectDataBase():

    # Create a database connection object using psycopg2
    # --> add your Python code here
    try:
        connection = psycopg2.connect(
            database="corpus",
            user="psotgres",
            password="921401",
            host="localhost",
            port="5432"
        )
        return connection
    except psycopg2.Error as e:
        print("Error connecting to the database:", e)
        return None

def createCategory(cur, catId, catName):

    # Insert a category in the database
    # --> add your Python code here

    query = "INSERT INTO categories (category_id, name) VALUES (%s, %s)"

    try:
        with cur:
            cur.execute(query, (catId, catName))
    except psycopg2.Error as e:
        print("Error creating the category:", e)

def createDocument(cur, docId, docText, docTitle, docDate, docCat):
    
    try:
        # 1 Get the category id based on the informed category name
        # --> add your Python code here
        cur.execute("SELECT category_id FROM categories WHERE name = %s", (docCat,))
        categoryId = cur.fetchone()[0]

        # 2 Insert the document in the database. For num_chars, discard the spaces and punctuation marks.
        # --> add your Python code here
        cleanedText = ''.join(char for char in docText if char.isalnum())
        numChars = len(cleanedText)

        cur.execute("INSERT INTO documents (doc_id, text, title, num_chars, date, category_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (docId, docText, docTitle, numChars, docDate, categoryId))

        # 3 Update the potential new terms.
        # 3.1 Find all terms that belong to the document. Use space " " as the delimiter character for terms and Remember to lowercase terms and remove punctuation marks.
        # 3.2 For each term identified, check if the term already exists in the database
        # 3.3 In case the term does not exist, insert it into the database
        # --> add your Python code here
        
        terms = [term.strip('.,!?').lower() for term in docText.split()]  # lowercase and remove punctuation
        for term in terms:
            numChars = len(term)
            cur.execute("INSERT INTO terms (term, num_chars) VALUES (%s, %s) ON CONFLICT DO NOTHING", (term, numChars))

        # 4 Update the index
        # 4.1 Find all terms that belong to the document
        # 4.2 Create a data structure the stores how many times (count) each term appears in the document
        # 4.3 Insert the term and its corresponding count into the database
        # --> add your Python code here
        
        termCounts = {term: terms.count(term) for term in set(terms)}  # Count occurrences using a set for uniqueness

        for term, count in termCounts.items():
            cur.execute("INSERT INTO index (term, doc_id, count) VALUES (%s, %s, %s)",
                        (term, docId, count))
    except psycopg2.Error as e:
        print("Error creating the document:", e)

def deleteDocument(cur, docId):
    try:
    # 1 Query the index based on the document to identify terms
    # 1.1 For each term identified, delete its occurrences in the index for that document
    # 1.2 Check if there are no more occurrences of the term in another document. If this happens, delete the term from the database.
    # --> add your Python code here
        cur.execute("SELECT term FROM index WHERE doc_id = %s", (docId,))
        terms = cur.fetchall()

        # 2 Delete the document from the database
        # --> add your Python code here
        cur.execute("DELETE FROM documents WHERE doc_id = %s", (docId,))

        for term in terms:
            cur.execute("UPDATE index SET count = count - 1 WHERE term = %s", (term[0],))
            cur.execute("DELETE FROM index WHERE term = %s AND count <= 0", (term[0],))

    except psycopg2.Error as e:
        print("Error deleting the document:", e)

def updateDocument(cur, docId, docText, docTitle, docDate, docCat):
    try:
        # 1. Delete the document
        cur.execute("SELECT term FROM index WHERE doc_id = %s", (docId,))
        terms = cur.fetchall()
        cur.execute("DELETE FROM documents WHERE doc_id = %s", (docId,))

        # 2. Create the document with the same ID
        cur.execute("SELECT category_id FROM categories WHERE name = %s", (docCat,))
        category_id = cur.fetchone()[0]

        cleaned_text = ''.join(char for char in docText if char.isalnum())
        num_chars = len(cleaned_text)

        cur.execute("INSERT INTO documents (doc_id, text, title, num_chars, date, category_id) VALUES (%s, %s, %s, %s, %s, %s)",
                    (docId, docText, docTitle, num_chars, docDate, category_id))

        terms_to_insert = [term.strip('.,!?').lower() for term in docText.split()]  
        for term in set(terms + terms_to_insert): 
            num_chars = len(term)
            cur.execute("INSERT INTO terms (term, num_chars) VALUES (%s, %s) ON CONFLICT DO NOTHING", (term, num_chars))

        term_counts = {term: terms_to_insert.count(term) for term in set(terms_to_insert)} 

        for term, count in term_counts.items():
            cur.execute("INSERT INTO index (term, doc_id, count) VALUES (%s, %s, %s)",
                        (term, docId, count))

        for term in terms:
            cur.execute("UPDATE index SET count = count - 1 WHERE term = %s", (term[0],))
            cur.execute("DELETE FROM index WHERE term = %s AND count <= 0", (term[0],))

    except psycopg2.Error as e:
        print("Error updating the document:", e)



def getIndex(cur):

    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    # --> add your Python code here

    inverted_index = {}
    try:
        # Modify the SQL query to match your table structure
        query = """
            SELECT term, array_agg(documents.title || ':' || count)
            FROM index
            INNER JOIN documents ON index.doc_id = documents.doc_id
            GROUP BY term
            ORDER BY term
        """
        cur.execute(query)
        rows = cur.fetchall()

        for row in rows:
            term, counts = row
            inverted_index[term] = ','.join(counts)
    except psycopg2.Error as e:
        print("Error retrieving the inverted index:", e)

    return inverted_index