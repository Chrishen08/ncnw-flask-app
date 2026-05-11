from flask import Flask, request, jsonify, render_template, redirect, url_for
import sqlite3
from datetime import datetime

app = Flask(__name__)

def get_db():
    conn = sqlite3.connect("ncnw.db")
    conn.row_factory = sqlite3.Row
    return conn



# HOME

@app.route("/")
def home():
    return "NCNW API Running"



# APPLICATION FORM

@app.route("/application")
def application_form():
    return render_template("application.html")



# ✅ NEW SUCCESS PAGE

@app.route("/application_success")
def application_success():
    return render_template("application_success.html")



# SUBMIT APPLICATION

@app.route("/submit_application", methods=["POST"])
def submit_application():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO applications (
            application_date,
            first_name,
            last_name,
            email,
            phone,
            address,
            city,
            state,
            zip,
            member_status,
            membership_type_id,
            comments,
            application_status,
            submitted_at
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        datetime.now().strftime("%Y-%m-%d"),
        request.form.get("first_name"),
        request.form.get("last_name"),
        request.form.get("email"),
        request.form.get("phone"),
        request.form.get("address"),
        request.form.get("city"),
        request.form.get("state"),
        request.form.get("zip"),
        request.form.get("member_status"),
        request.form.get("membership_type_id"),
        request.form.get("comments"),
        "Pending",
        datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    ))

    conn.commit()
    conn.close()

    # ✅ REDIRECT TO SUCCESS PAGE
    return redirect(url_for('application_success'))



# ADMIN DASHBOARD

@app.route("/admin")
def admin_dashboard():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            applications.*,
            membership_types.type_name AS membership_type
        FROM applications
        LEFT JOIN membership_types
        ON applications.membership_type_id = membership_types.membership_type_id
        ORDER BY submitted_at DESC
    """)

    applications = cursor.fetchall()
    conn.close()

    return render_template("admin.html", applications=applications)



# MARK PAYMENT RECEIVED

@app.route("/mark_paid/<int:application_id>", methods=["POST"])
def mark_paid(application_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM applications WHERE application_id = ?", (application_id,))
    app_data = cursor.fetchone()

    cursor.execute("SELECT * FROM members WHERE application_id = ?", (application_id,))
    if cursor.fetchone():
        conn.close()
        return redirect(url_for('admin_dashboard'))

    cursor.execute("""
        INSERT INTO members (
            first_name, last_name, email, phone,
            address, city, state, zip,
            member_status, membership_type_id,
            role_id, date_joined, active_status, application_id
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        app_data["first_name"],
        app_data["last_name"],
        app_data["email"],
        app_data["phone"],
        app_data["address"],
        app_data["city"],
        app_data["state"],
        app_data["zip"],
        app_data["member_status"],
        app_data["membership_type_id"],
        3,
        datetime.now().strftime("%Y-%m-%d"),
        "Active",
        application_id
    ))

    cursor.execute("""
        UPDATE applications
        SET application_status = 'Paid'
        WHERE application_id = ?
    """, (application_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))



# DELETE APPLICATION

@app.route("/delete_application/<int:application_id>", methods=["POST"])
def delete_application(application_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM members WHERE application_id = ?", (application_id,))
    cursor.execute("DELETE FROM applications WHERE application_id = ?", (application_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('admin_dashboard'))



# MEMBERS PAGE

@app.route("/members")
def members_page():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT members.*, membership_types.type_name AS membership_type
        FROM members
        LEFT JOIN membership_types
        ON members.membership_type_id = membership_types.membership_type_id
    """)

    members = cursor.fetchall()
    conn.close()

    return render_template("members.html", members=members)



# DELETE MEMBER

@app.route("/delete_member/<int:member_id>", methods=["POST"])
def delete_member(member_id):
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("DELETE FROM members WHERE member_id = ?", (member_id,))

    conn.commit()
    conn.close()

    return redirect(url_for('members_page'))



# RUN

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)