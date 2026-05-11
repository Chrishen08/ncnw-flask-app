import sqlite3

DB_NAME = "ncnw.db"

def create_connection():
    return sqlite3.connect(DB_NAME)

def create_tables(cursor):

    # Membership types table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS membership_types (
        membership_type_id INTEGER PRIMARY KEY AUTOINCREMENT,
        type_name TEXT UNIQUE,
        total_fee REAL,
        local_dues REAL,
        national_dues REAL,
        recurring_annual_dues_required INTEGER,
        description TEXT
    )
    """)

    # Roles table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS roles (
        role_id INTEGER PRIMARY KEY AUTOINCREMENT,
        role_name TEXT UNIQUE,
        description TEXT
    )
    """)

    # Applications table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS applications (
        application_id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_date TEXT,
        first_name TEXT,
        last_name TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        phone TEXT,
        email TEXT,
        member_status TEXT,
        member_number TEXT,
        membership_type_id INTEGER,
        comments TEXT,
        application_status TEXT,
        submitted_at TEXT
    )
    """)

    # Members table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS members (
        member_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT,
        last_name TEXT,
        address TEXT,
        city TEXT,
        state TEXT,
        zip TEXT,
        phone TEXT,
        email TEXT,
        member_status TEXT,
        member_number TEXT,
        membership_type_id INTEGER,
        role_id INTEGER,
        date_joined TEXT,
        active_status TEXT,
        application_id INTEGER
    )
    """)

    # Payments table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS payments (
        payment_id INTEGER PRIMARY KEY AUTOINCREMENT,
        application_id INTEGER,
        member_id INTEGER,
        membership_type_id INTEGER,
        payment_amount REAL,
        local_dues REAL,
        national_dues REAL,
        payment_method TEXT,
        payment_status TEXT,
        payment_date TEXT,
        notes TEXT
    )
    """)


def seed_reference_data(cursor):

    membership_types = [
        ("Annual", 95.00, 20.00, 75.00, 1, "Standard annual membership"),
        ("Life", 1020.00, 20.00, 1000.00, 0, "One-time life membership"),
        ("Legacy Life", 1520.00, 20.00, 1500.00, 0, "One-time legacy life membership"),
        ("Per Capita", 45.00, 20.00, 25.00, 1, "Per capita membership")
    ]

    roles = [
        ("Administrator", "System admin"),
        ("Executive Board", "Leadership"),
        ("Regular Member", "Standard member")
    ]

    cursor.executemany("""
    INSERT OR IGNORE INTO membership_types
    (type_name, total_fee, local_dues, national_dues, recurring_annual_dues_required, description)
    VALUES (?, ?, ?, ?, ?, ?)
    """, membership_types)

    cursor.executemany("""
    INSERT OR IGNORE INTO roles
    (role_name, description)
    VALUES (?, ?)
    """, roles)


def main():
    conn = create_connection()
    cursor = conn.cursor()

    create_tables(cursor)
    seed_reference_data(cursor)

    conn.commit()
    conn.close()

    print("Database and tables created successfully.")


if __name__ == "__main__":
    main()


