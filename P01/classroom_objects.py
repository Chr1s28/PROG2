#Represent contents of a typical classroom (table, blackboard, student, teacher,
#document) as Python class structures, each with class name, constructor method and
#attributes. Some attributes may cross-reference objects of other classes. Instantiate the
#classes as multiple objects, using range iterations if adequate, to represent the following
#scenario: The teacher has 20 copies of a document. There are 10 tables, and each
#table is occupied by two students. Each document belongs to one of the students. On
#the blackboard, the name of the teacher is written.


class Teacher:
    def __init__(self,name):
        self.name = name
        self.documents = [Document(doc_id=i+1) for i in range(20)]
    
    def __repr__(self):
        return f"Teacher(name='{self.name}')"
    
class Document:
    def __init__(self, doc_id, owner=None):
        self.doc_id = doc_id
        self.owner = owner

    def __repr__(self):
        if self.owner:
            owner_name = self.owner.name  
        else: 
            owner_name = "None"
        return f"Document(id = {self.doc_id}, owner = {owner_name})"

class Student:
    def __init__(self, name, table, document):
        self.name = name
        self.table = table
        self.document = document
    def __repr__(self):
        if self.table:
            table_id = self.table_id
        else:
            table_id = "None"
        if self.doc_id:
            doc_id = self.doc_id
        else:
            doc_id = "None"

class Table:
    def __init__(self, table_id):
        self.table_id = table_id
        self.students = []

    def __repr__(self):
        return f"Table(id = {self.table_id}, students = {[student.name for student in self.students]})"
    
class Blackboard:
    def __init__(self, blackboard_id, content):
        self.blackboard_id = blackboard_id
        self.content = content
    
    def __repr__(self):
        return f"Blackboard(id = {self.blackboard_id}, content = {self.content})"
    

teacher_meier = Teacher("Meier")
blackboard = Blackboard(1, teacher_meier.name)
tables = [Table(table_id=i+1) for i in range(10)]
students = []
doc_index = 0 

for table in tables:
    # For each table, create two students.
    for i in range(2):
        student_name = f"Student_{table.table_id}_{i+1}"
        # Get the next available document from the teacher's documents.
        doc = teacher_meier.documents[doc_index]
        doc.owner = None  # Temporarily clear owner
        # Create the student with the table reference and document.
        student = Student(name=student_name, table=table, document=doc)
        # Now, assign the document's owner as this student.
        doc.owner = student
        
        # Add student to the table and to the global student list.
        table.students.append(student)
        students.append(student)
        
        doc_index += 1

# -------------------------------------------------------------------
# Output a summary of the created objects

print("Teacher:", teacher_meier)
print("Blackboard:", blackboard)
print("\nTables and their students:")
for table in tables:
    print(table)

print("\nA few sample documents:")
# Print first 5 documents to check ownership
for doc in teacher_meier.documents[:5]:
    print(doc)