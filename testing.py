from pymongo import MongoClient

# connect to the MongoDB on MongoLab
# to learn more about MongoLab visit http://www.mongolab.com
# replace the "" in the line below with your MongoLab connection string
# you can also use a local MongoDB instance
connection = MongoClient("mongodb://a0c62639a010d4b369c993fee9cef755:85a89404d4d9f59a3a4382b430b48b5b@10.11.57.208:27017,10.11.57.209:27017,10.11.57.210:27017/a8f04fca2fc74de2?replicaSet=cab90fcbfb16d3718f8ecb48c71a06c4")

# connect to the students database and the ctec121 collection
db = connection.students.ctec121

# create a dictionary to hold student documents

# create dictionary
student_record = {}

# set flag variable
flag = True

# loop for data input
while (flag):
    # ask for input
    student_name, student_grade = input("Enter student name and grade: ").split(',')
    # place values in dictionary
    student_record = {'name': student_name, 'grade': student_grade}
    # insert the record
    db.insert(student_record)
    # should we continue?
    flag = input('Enter another record? ')
    if (flag[0].upper() == 'N'):
        flag = False

# find all documents
results = db.find()

print()
print('+-+-+-+-+-+-+-+-+-+-+-+-+-+-')

# display documents from collection
for record in results:
# print out the document
    print(record['name'] + ',', record['grade'])

print()

# close the connection to MongoDB
connection.close()