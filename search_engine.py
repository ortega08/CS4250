#-------------------------------------------------------------------------
# AUTHOR: Jessica Ortega
# FILENAME: search_engine.py
# SPECIFICATION: description of the program
# FOR: CS 4250- Assignment #1
# TIME SPENT: how long it took you to complete the assignment
#-----------------------------------------------------------*/

#IMPORTANT NOTE: DO NOT USE ANY ADVANCED PYTHON LIBRARY TO COMPLETE THIS CODE SUCH AS numpy OR pandas. You have to work here only with standard arrays

#importing some Python libraries
import csv
import math 

documents = []
labels = []

#reading the data in a csv file
with open('collection.csv', 'r') as csvfile:
  reader = csv.reader(csvfile)
  for i, row in enumerate(reader):
         if i > 0:  # skipping the header
            documents.append (row[0])
            labels.append(row[1])

#Conduct stopword removal.
#--> add your Python code here
stopWords = {'I', 'and', 'She', 'They', 'her', 'their'}
for i, document in enumerate(documents):
    documents[i] = document.split()

for i, document in enumerate(documents):
    documents[i] = [term for term in document if term not in stopWords]

#Conduct stemming.
#--> add your Python code here
steeming = {
  "cats": "cat",
  "dogs": "dog",
  "loves": "love",
}

for i, document in enumerate(documents):
    for j, term in enumerate(document):
        if term in steeming:
            documents[i][j] = steeming[term]

#Identify the index terms.
#--> add your Python code here
terms = []
for document in documents:
    for term in document:
        if term not in terms:
            terms.append(term)

#Build the tf-idf term weights matrix.
#--> add your Python code here
docMatrix = []
for doc in documents:
    docRow = []
    docLen = len(doc)
    for term in terms:
        tf = doc.count(term) / docLen
        df = sum(1 for doc in documents if term in doc)
        idf = math.log10(len(documents) / (1 + df))
        tfidf = tf * idf
        docRow.append(tfidf)
    docMatrix.append(docRow)

#Calculate the document scores (ranking) using document weigths (tf-idf) calculated before and query weights (binary - have or not the term).
#--> add your Python code here
query = "cat and dog"
queryTerms = ['cat', 'dog']
docScores = []

for docWeights in docMatrix:
    score = 0
    for queryTerm in queryTerms:
        termIndex = terms.index(queryTerm) if queryTerm in terms else -1
        if termIndex >= 0:
          score += docWeights[termIndex]
    docScores.append(score)

#Calculate and print the precision and recall of the model by considering that the search engine will return all documents with scores >= 0.1.
#--> add your Python code here
threshold = 0.1

hits = 0
misses = 0
noise = 0

for i in range(len(docScores)):
    score = docScores[i]
    label = labels[i]

    if score > threshold:
        if label == 'R':
          hits += 1
        elif label == 'I':
          noise += 1
    else:
        if label == 'R':
          misses += 1

recallDen = hits + noise
if recallDen == 0:
  recall = 0 
else:
  recall = (hits / recallDen) * 100

precisionDen = hits + noise
if precisionDen == 0:
  precision = 0  
else:
  precision = (hits / precisionDen) * 100

print("Precision: {}%".format(precision))
print("Recall: {}%".format(recall))

