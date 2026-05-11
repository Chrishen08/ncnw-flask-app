from tkinter import simpledialog, messagebox
from tkinter import *
import gradebook



root = Tk()
root.title("Ms.Carter's Electronic Gradebook")

screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
root.geometry(f"{int(screen_width * 0.9)}x{int(screen_height * 0.9)}")

TITLE_FONT = ("Helvetica", 22, "bold")
BUTTON_FONT = ("Helvetica", 14)

root.configure(bg="#ECEFF1")  # soft gray

main_frame = Frame(
    root,
    bg="gray",
    padx=45,
    pady=45
)
main_frame.pack(expand=True)

Label(
    main_frame,
    text="Ms. Carter's Electronic Gradebook",
    font=TITLE_FONT,
    bg="gray",
    fg="#263238"
).pack(pady=(0, 20))

def make_button(root, text, command):
    return Button(
        main_frame,
        text=text,
        command=command,
        font=BUTTON_FONT,
        fg="Black",
        relief="raised",
        activebackground="#1565C0",
        activeforeground="white",
        bd=1,
        padx=10,
        pady=10
    )


def gui_add_new_student():
    conn = gradebook.connect_db()
    cursor = conn.cursor()

    student_id = simpledialog.askinteger("Add Student", "Enter Student ID:")
    if student_id is None:
        conn.close()
        return

    first_name = simpledialog.askstring("Add Student", "Enter Student first name:")
    if first_name is None:
        conn.close()
        return

    last_name = simpledialog.askstring("Add Student", "Enter Student last name:")
    if last_name is None:
        conn.close()
        return

    cursor.execute("""
    INSERT OR REPLACE INTO Students (student_id, first_name, last_name)
    VALUES (?, ?, ?);
    """, (student_id, first_name, last_name))

    conn.commit()

    messagebox.showinfo("Success", "Student saved successfully.")
    conn.close()


make_button(root, "Add Student", gui_add_new_student).pack(fill="x", pady=6)


def gui_enroll_student():
    conn = gradebook.connect_db()
    cursor = conn.cursor()

    student_id = simpledialog.askinteger("Enroll Student", "Enter Student ID:")
    if student_id is None:
        conn.close()
        return

    class_id = simpledialog.askinteger("Enroll Student", "Enter Class ID:")
    if class_id is None:
        conn.close()
        return

    cursor.execute("""
    INSERT OR IGNORE INTO Enrollments (student_id, class_id)
    VALUES (?, ?);
    """, (student_id, class_id))

    conn.commit()

    messagebox.showinfo("Success", "Enrollment saved (if IDs exist).")
    conn.close()


make_button(root, text="Enroll Student",command=gui_enroll_student).pack(fill="x", pady=6)


def gui_add_assignment():
    conn = gradebook.connect_db()
    cursor = conn.cursor()

    class_id = simpledialog.askinteger("Add Assignment", "Enter Class ID:")
    if class_id is None:
        conn.close()
        return

    assignment_name = simpledialog.askstring("Add Assignment", "Enter Assignment Name:")
    if assignment_name is None:
        conn.close()
        return

    points_possible = simpledialog.askinteger("Add Assignment", "Enter Points Possible:")
    if points_possible is None:
        conn.close()
        return

    cursor.execute("""
    INSERT INTO Assignments (class_id, assignment_name, points_possible)
    VALUES (?, ?, ?);
    """, (class_id, assignment_name, points_possible))

    conn.commit()

    messagebox.showinfo("Success", "Assignment saved successfully.")
    conn.close()


make_button(root, text="Add Assignment", command=gui_add_assignment).pack(fill="x", pady=6)


def gui_add_or_update_submission():
    conn = gradebook.connect_db()
    cursor = conn.cursor()

    # Student + class
    student_id = simpledialog.askinteger("Submission", "Enter Student ID:")
    if student_id is None:
        conn.close()
        return

    class_id = simpledialog.askinteger("Submission", "Enter Class ID:")
    if class_id is None:
        conn.close()
        return

    # Validate enrollment
    cursor.execute("""
    SELECT 1 FROM Enrollments
    WHERE student_id = ? AND class_id = ?;
    """, (student_id, class_id))

    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Student is not enrolled in this class.")
        conn.close()
        return

    # Show assignments 
    assignments = gradebook.list_assignments_for_class(cursor, class_id)
    if not assignments:
        messagebox.showerror("Error", "No assignments found for this class.")
        conn.close()
        return

    assignment_list = ""
    for aid, name, pts in assignments:
        assignment_list += f"ID {aid}: {name} ({pts} pts)\n"

    messagebox.showinfo("Assignments", assignment_list)

    # Assignment ID
    assignment_id = simpledialog.askinteger("Submission", "Enter Assignment ID:")
    if assignment_id is None:
        conn.close()
        return

    submitted = simpledialog.askstring("Submission", "Submitted? (yes/no):")
    if submitted is None:
        conn.close()
        return

    submitted = submitted.strip().lower()

    if submitted == "yes":
        score = simpledialog.askfloat("Submission", "Enter score earned:")
        if score is None:
            conn.close()
            return
        status = "submitted"
    else:
        score = 0
        status = "missing"

    # Check if submission already exists
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
        messagebox.showinfo("Success", "Submission updated.")
    else:
        cursor.execute("""
        INSERT INTO Submissions (student_id, assignment_id, score, status)
        VALUES (?, ?, ?, ?);
        """, (student_id, assignment_id, score, status))
        messagebox.showinfo("Success", "Submission added.")

    conn.commit()
    conn.close()



make_button(root, text="Add / Update Grade",command=gui_add_or_update_submission).pack(fill="x", pady=6)

def gui_view_progress_report():
    conn = gradebook.connect_db()
    cursor = conn.cursor()

    student_id = simpledialog.askinteger("Progress Report", "Enter Student ID:")
    if student_id is None:
        conn.close()
        return

    class_id = simpledialog.askinteger("Progress Report", "Enter Class ID:")
    if class_id is None:
        conn.close()
        return

    cursor.execute("""
    SELECT 1
    FROM Enrollments
    WHERE student_id = ? AND class_id = ?;
    """, (student_id, class_id))

    if cursor.fetchone() is None:
        messagebox.showerror("Error", "Student is not enrolled in this class.")
        conn.close()
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

    earned, possible, percent = gradebook.get_current_grade(cursor, student_id, class_id)
    missing = gradebook.get_missing_assignments(cursor, student_id, class_id)

    report = (
        f"Student: {student_name} (ID: {student_id})\n"
        f"Class:   {class_name} (ID: {class_id})\n"
        f"Grade:   {percent:.2f}% ({earned}/{possible})\n\n"
    )

    if not missing:
        report += "Missing assignments: None"
    else:
        report += "Missing assignments:\n"
        for _, name, points in missing:
            report += f"- {name} ({points} pts)\n"

    messagebox.showinfo("Progress Report", report)
    conn.close()


make_button(root, text="View Progress Report", command=gui_view_progress_report).pack(fill="x", pady=6)


def gui_view_struggling_students():
    conn = gradebook.connect_db()
    cursor = conn.cursor()

    class_id = simpledialog.askinteger(
        "Struggling Students", "Enter Class ID:"
    )
    if class_id is None:
        conn.close()
        return

    threshold = simpledialog.askfloat(
        "Struggling Students", "Enter grade threshold (ex: 70):"
    )
    if threshold is None:
        conn.close()
        return

    struggling = gradebook.list_struggling_students(
        cursor, class_id, threshold
    )

    if not struggling:
        messagebox.showinfo(
            "Struggling Students",
            "No struggling students found."
        )
        conn.close()
        return

    result = "Struggling students:\n\n"
    for student_id, pct in struggling:
        result += f"- Student {student_id}: {pct:.2f}%\n"

    messagebox.showinfo("Struggling Students", result)
    conn.close()


make_button(root, text="Sturggling Students", command=gui_view_struggling_students).pack(fill="x", pady=6)



Button(
    main_frame,
    text="Exit",
    command=root.quit,
    font=BUTTON_FONT,
    fg="black",
    relief="raised",
    bd=0,
    pady=10
).pack(fill="x", pady=(20, 0))




root.mainloop()