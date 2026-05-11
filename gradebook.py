import sqlite3

DB_NAME = "/Users/chrishenry/Desktop/System Design/gradebook.db"



# Database connection 

def connect_db():
    conn = sqlite3.connect(DB_NAME)
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn






# Table creation

def create_tables(cursor):
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Students (
        student_id INTEGER PRIMARY KEY,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Classes (
        class_id INTEGER PRIMARY KEY,
        course_name TEXT
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Enrollments (
        student_id INTEGER NOT NULL,
        class_id INTEGER NOT NULL,
        PRIMARY KEY (student_id, class_id),
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (class_id) REFERENCES Classes(class_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Assignments (
        assignment_id INTEGER PRIMARY KEY,
        class_id INTEGER NOT NULL,
        assignment_name TEXT NOT NULL,
        points_possible INTEGER NOT NULL,
        FOREIGN KEY (class_id) REFERENCES Classes(class_id)
    );
    """)

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS Submissions (
        submission_id INTEGER PRIMARY KEY,
        student_id INTEGER NOT NULL,
        assignment_id INTEGER NOT NULL,
        score REAL DEFAULT 0,
        status TEXT NOT NULL CHECK(status IN ('submitted', 'missing')),
        UNIQUE (student_id, assignment_id),
        FOREIGN KEY (student_id) REFERENCES Students(student_id),
        FOREIGN KEY (assignment_id) REFERENCES Assignments(assignment_id)
    );
    """)
    



# Core grade logic

def get_current_grade(cursor, student_id, class_id):
    cursor.execute("""
    SELECT
      COALESCE(SUM(s.score), 0) AS earned,
      COALESCE(SUM(a.points_possible), 0) AS possible
    FROM Assignments a
    LEFT JOIN Submissions s
      ON s.assignment_id = a.assignment_id
      AND s.student_id = ?
      AND s.status = 'submitted'
    WHERE a.class_id = ?;
    """, (student_id, class_id))

    earned, possible = cursor.fetchone()

    if possible == 0:
        return 0, 0, 0.0

    percent = (earned / possible) * 100
    return earned, possible, percent


def get_missing_assignments(cursor, student_id, class_id):
    cursor.execute("""
    SELECT DISTINCT
      a.assignment_id,
      a.assignment_name,
      a.points_possible
    FROM Assignments a
    LEFT JOIN Submissions s
      ON s.assignment_id = a.assignment_id
      AND s.student_id = ?
    WHERE a.class_id = ?
      AND (s.submission_id IS NULL OR s.status != 'submitted');
    """, (student_id, class_id))

    return cursor.fetchall()


def list_struggling_students(cursor, class_id, threshold=70):
    cursor.execute("""
    SELECT student_id
    FROM Enrollments
    WHERE class_id = ?;
    """, (class_id,))

    students = cursor.fetchall()
    struggling = []

    for (student_id,) in students:
        earned, possible, percent = get_current_grade(cursor, student_id, class_id)

        if possible == 0:
            continue

        if earned == 0:
            continue

        if percent <= threshold:
            struggling.append((student_id, percent))

    return struggling



# Teacher "add" functions

def add_new_student(cursor):
    student_id = int(input("Enter student ID: ").strip())
    first_name = input("Enter first name: ").strip()
    last_name = input("Enter last name: ").strip()

    cursor.execute("""
    INSERT OR REPLACE INTO Students (student_id, first_name, last_name)
    VALUES (?, ?, ?);
    """, (student_id, first_name, last_name))

    print("Student saved.")


def enroll_student(cursor):
    student_id = int(input("Enter student ID: ").strip())
    class_id = int(input("Enter class ID: ").strip())

    cursor.execute("""
    INSERT OR IGNORE INTO Enrollments (student_id, class_id)
    VALUES (?, ?);
    """, (student_id, class_id))

    print("Enrollment saved (if IDs exist).")


def add_assignment(cursor):
    class_id = int(input("Enter class ID: ").strip())
    assignment_name = input("Assignment name: ").strip()
    points_possible = int(input("Points possible: ").strip())

    cursor.execute("""
    INSERT INTO Assignments (class_id, assignment_name, points_possible)
    VALUES (?, ?, ?);
    """, (class_id, assignment_name, points_possible))

    print("Assignment saved.")


def list_assignments_for_class(cursor, class_id):
    cursor.execute("""
    SELECT assignment_id, assignment_name, points_possible
    FROM Assignments
    WHERE class_id = ?
    ORDER BY assignment_id;
    """, (class_id,))

    rows = cursor.fetchall()

    if not rows:
        print("No assignments found for this class.")
        return

    print("Assignments in this class:")
    for aid, name, pts in rows:
        print(f"- ID {aid}: {name} ({pts} pts)")


def add_or_update_submission(cursor):
    student_id = int(input("Enter student ID: ").strip())
    class_id = int(input("Enter class ID: ").strip())

    cursor.execute("""
    SELECT 1 FROM Enrollments
    WHERE student_id = ? AND class_id = ?;
    """, (student_id, class_id))

    if cursor.fetchone() is None:
        print("Student is not enrolled in this class.")
        return

    list_assignments_for_class(cursor, class_id)

    assignment_id = int(input("Enter assignment ID: ").strip())
    submitted = input("Submitted? (yes/no): ").strip().lower()

    if submitted == "yes":
        score = float(input("Score earned: ").strip())
        status = "submitted"
    else:
        score = 0
        status = "missing"

    cursor.execute("""
    SELECT submission_id
    FROM Submissions
    WHERE student_id = ? AND assignment_id = ?;
    """, (student_id, assignment_id))

    row = cursor.fetchone()

    if row:
        cursor.execute("""
        UPDATE Submissions
        SET score = ?, status = ?
        WHERE student_id = ? AND assignment_id = ?;
        """, (score, status, student_id, assignment_id))
        print("Submission updated.")
    else:
        cursor.execute("""
        INSERT INTO Submissions (student_id, assignment_id, score, status)
        VALUES (?, ?, ?, ?);
        """, (student_id, assignment_id, score, status))
        print("Submission added.")



# Reports

def view_progress_report(cursor):
    student_id = int(input("Enter student ID: ").strip())
    class_id = int(input("Enter class ID: ").strip())

    cursor.execute("""
    SELECT 1
    FROM Enrollments
    WHERE student_id = ? AND class_id = ?;
    """, (student_id, class_id))

    if cursor.fetchone() is None:
        print("Student is not enrolled in this class.")
        return

    cursor.execute("""
    SELECT first_name, last_name
    FROM Students
    WHERE student_id = ?;
    """, (student_id,))
    row = cursor.fetchone()
    student_name = f"{row[0]} {row[1]}" if row else "Unknown Student"

    cursor.execute("""
    SELECT course_name
    FROM Classes
    WHERE class_id = ?;
    """, (class_id,))
    row = cursor.fetchone()
    class_name = row[0] if row else "Unknown Class"

    earned, possible, percent = get_current_grade(cursor, student_id, class_id)
    missing = get_missing_assignments(cursor, student_id, class_id)

    print("\n=== Progress Report ===")
    print(f"Student: {student_name} (ID: {student_id})")
    print(f"Class:   {class_name} (ID: {class_id})")
    print(f"Grade:   {percent:.2f}% ({earned}/{possible})")

    if not missing:
        print("Missing assignments: None")
    else:
        print("Missing assignments:")
        for _, name, points in missing:
            print(f"- {name} ({points} pts)")
    print()


def view_struggling_students(cursor):
    class_id = int(input("Enter class ID: ").strip())
    threshold = float(input("Struggling threshold (ex: 70): ").strip())

    struggling = list_struggling_students(cursor, class_id, threshold)

    if not struggling:
        print("No struggling students found.")
        return

    print("Struggling students:")
    for student_id, pct in struggling:
        print(f"- Student {student_id}: {pct:.2f}")
def menu():
    conn = connect_db()
    cursor = conn.cursor()

   


    create_tables(cursor)
    conn.commit()

    while True:
        print("\nMs. Carter's Electronic Gradebook")
        print("1. Add Student")
        print("2. Enroll Student in Class")
        print("3. Add Assignment")
        print("4. Add/Update Grade (Submission)")
        print("5. View Progress Report")
        print("6. Identify Struggling Students")
        print("7. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            add_new_student(cursor)
            conn.commit()
        elif choice == "2":
            enroll_student(cursor)
            conn.commit()
        elif choice == "3":
            add_assignment(cursor)
            conn.commit()
        elif choice == "4":
            add_or_update_submission(cursor)
            conn.commit()
        elif choice == "5":
            view_progress_report(cursor)
        elif choice == "6":
            view_struggling_students(cursor)
        elif choice == "7":
            break
        else:
            print("Invalid option.")

    conn.close()


if __name__ == "__main__":
    menu()
