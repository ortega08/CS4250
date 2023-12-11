#-------------------------------------------------------------------------
# AUTHOR: Jessica Ortega
# FILENAME: db_connection_mongo_solution.py
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #2
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with
# standard arrays

#importing some Python libraries
# --> add your Python code here

import pymongo

def connectDataBase():

    # Create a database connection object using pymongo
    # --> add your Python code here

    try:
        # Create a database connection
        client = pymongo.MongoClient("mongodb://localhost:27017/corpus")
        db = client["corpus"]
        return db
    except Exception as e:
        print("Error connecting to MongoDB:", e)
        return None


def createDocument(col, docId, docText, docTitle, docDate, docCat):
    try:
        # create a dictionary to count how many times each term appears in the document.
        # Use space " " as the delimiter character for terms and remember to lowercase them.
        # --> add your Python code here
        
        category_doc = col.database["categories"].find_one({"name": docCat})
        if category_doc is None:
            category_doc = {
                "name": docCat,
            }
            col.database["categories"].insert_one(category_doc)

        termCounts = {}
        terms = [term.strip('.,!?').lower() for term in docText.split()]

        for term in terms:
            termCounts[term] = termCounts.get(term, 0) + 1

        # create a list of dictionaries to include term objects.
        # --> add your Python code here
        termObjects = [{"term": term, "count": count} for term, count in termCounts.items()]

        #Producing a final document as a dictionary including all the required document fields
        # --> add your Python code here
        categoryId = col.database["categories"].find_one({"name": docCat})["_id"]
        cleanedText = ''.join(char for char in docText if char.isalnum())
        numChars = len(cleanedText)
        document = {
            "doc_id": docId,
            "text": docText,
            "title": docTitle,
            "num_chars": numChars,
            "date": docDate,
            "category_id": categoryId,
            "terms": termObjects
        }

        # Insert the document
        # --> add your Python code here
        col.insert_one(document)

    except Exception as e:
        print("Error creating the document:", e)



def deleteDocument(col, docId):

    # Delete the document from the database
    # --> add your Python code here
    try:
        col.delete_one({"doc_id": docId})
    except Exception as e:
        print("Error deleting the document:", e)


def updateDocument(col, docId, docText, docTitle, docDate, docCat):
    try:
        # Delete the document
        # --> add your Python code here

        # Create the document with the same id
        # --> add your Python code here
        category_doc = col.database["categories"].find_one({"name": docCat})
        if category_doc is None:
            category_doc = {
                "name": docCat,
            }
            col.database["categories"].insert_one(category_doc)

        category_id = col.database["categories"].find_one({"name": docCat})["_id"]
        cleanedText = ''.join([char for char in docText if char.isalnum()])
        numChars = len(cleanedText)
        document = {
            "doc_id": docId,
            "text": docText,
            "title": docTitle,
            "num_chars": numChars,
            "date": docDate,
            "category_id": category_id,
        }

        col.insert_one(document)
        termCounts = {}
        terms = [term.strip('.,!?').lower() for term in docText.split()]

        for term in terms:
            if term in termCounts:
                termCounts[term] += 1
            else:
                termCounts[term] = 1

        termObjects = [{"term": term, "count": count} for term, count in termCounts.items()]

        col.update_one({"doc_id": docId}, {"$set": {"terms": termObjects}})
    except Exception as e:
        print("Error updating the document:", e)


def getIndex(col):
    # Query the database to return the documents where each term occurs with their corresponding count. Output example:
    # {'baseball':'Exercise:1','summer':'Exercise:1,California:1,Arizona:1','months':'Exercise:1,Discovery:3'}
    # ...
    # --> add your Python code here
    inverted_index = {}
    try:
        pipeline = [
            {"$unwind": "$terms"},
            {
                "$group": {
                    "_id": "$terms.term",
                    "counts": {"$push": {"title": "$title", "count": "$terms.count"}}
                }
            }
        ]

        result = list(col.aggregate(pipeline))

        for entry in result:
            term = entry["_id"]
            counts = entry["counts"]
            counts_str = ",".join([f"{item['title']}:{item['count']}" for item in counts])
            inverted_index[term] = counts_str

    except Exception as e:
        print("Error retrieving the inverted index:", e)

    return inverted_index
