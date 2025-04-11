class Document:
    """This is a class representation of a document.

    :param title: The title of the document
    :type title: str
    """

    def __init__(self, title: str):
        self.title = title
        self.owner: "ClassPerson" = None

    def __str__(self):
        return f"Document(title='{self.title}', owner='{self.owner.name if self.owner else None}')"


class Table:
    """This is a class representation of a table.

    :param number: The number of the table
    :type number: int
    """

    def __init__(self, number: int):
        self.number = number
        self.occupants: list["Student"] = []

    def __str__(self):
        return f"Table(number={self.number}, occupants={[occupant.name for occupant in self.occupants]})"


class Blackboard:
    """This is a class representation of a blackboard.

    :param content: The content written on the blackboard
    :type content: str
    """

    def __init__(self, content: str):
        self.content = content

    def __str__(self):
        return f"Blackboard(content='{self.content}')"


class ClassPerson:
    """This is a class representation of a person in the class.

    :param name: The name of the person
    :type name: str
    """

    def __init__(self, name: str):
        self.name = name
        self.documents: list[Document] = []

    def assign_document(self, document: Document):
        """Assigns a document to the person.

        If the document is already assigned to another person, it will be reassigned to this person.

        :param document: The document to be assigned
        :type document: Document
        """

        if document.owner:
            document.owner.documents.remove(document)

        document.owner = self
        self.documents.append(document)

    def __str__(self):
        return f"ClassPerson(name='{self.name}', documents={[doc.title for doc in self.documents]})"


class Student(ClassPerson):
    """This is a class representation of a student.

    :param name: The name of the student
    :type name: str
    """

    def __init__(self, name: str):
        self.table: Table = None
        super().__init__(name)

    def sit(self, table: Table):
        """Seats the student at a table.

        If the student is already seated at another table, they will be removed from that table first.

        :param table: The table at which the student will sit
        :type table: Table
        """

        if self.table:
            self.table.occupants.remove(self)

        self.table = table
        table.occupants.append(self)

    def __str__(self):
        return f"Student(name='{self.name}', documents={[doc.title for doc in self.documents]})"


class Teacher(ClassPerson):
    """This is a class representation of a teacher.

    :param name: The name of the teacher
    :type name: str
    """

    def __init__(self, name: str):
        super().__init__(name)

    def __str__(self):
        return f"Teacher(name='{self.name}', documents={[doc.title for doc in self.documents]})"


if __name__ == "__main__":
    # create teacher
    teacher = Teacher("Mr. Roth")

    # teacher writes on blackboard
    blackboard = Blackboard(f"Hi class, my name is '{teacher.name}'")

    # teacher creates copies of documents
    for i in range(20):
        teacher.assign_document(Document(f"Document {i}"))

    # create tables
    tables = [Table(i + 1) for i in range(10)]

    # create students
    students = [Student(f"Student {i}") for i in range(20)]

    # students are seated at tables
    for student in students:
        for table in tables:
            if len(table.occupants) < 2:
                student.sit(table)
                break

    # documents are handed out to students
    for i, document in enumerate(teacher.documents[:]):
        students[i].assign_document(document)

    # Classroom showcase
    print("===Classroom===")
    print(f"Blackboard: {blackboard.content}")
    print(f"Teacher: {teacher}")

    print("Tables:")
    for table in tables:
        print(f"  {table}")

    print("Students:")
    for student in students:
        print(f"  {student}")
