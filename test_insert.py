import sqlite3
from datetime import date 

conn = sqlite3.connect("ncnw.db")
cursor = conn.cursor()

#Sample app

cursor.execute("""
INSERT INTO applications (
    first_name, last_name, email, phone, address,
    membership_type, status, submitted_at
)
VALUES (?, ?, ?, ?, ?, ?, ?, ?)
""", (
    "Christian",
    "Henry",
    "chris@example.com",
    "555-123-4567",
    "123 Main St, Winston-Salem, NC",
    "Annual",
    "pending",
    str(date.today())
))

conn.commit()
conn.close()

print("Sample application inserted successfully.")