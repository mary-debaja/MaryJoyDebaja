
import sqlite3

conn = sqlite3.connect('students.db')
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS students (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id TEXT NOT NULL,
    name TEXT NOT NULL,
    program TEXT NOT NULL,
    year INTEGER NOT NULL,
    section TEXT NOT NULL,
    source TEXT DEFAULT 'Local'
)
''')

# Add source column if the existing table does not have it
cursor.execute("PRAGMA table_info(students)")
columns = [column[1] for column in cursor.fetchall()]

if 'source' not in columns:
    cursor.execute(
        "ALTER TABLE students ADD COLUMN source TEXT DEFAULT 'Local'"
    )

# Clear existing student records
cursor.execute("DELETE FROM students")

# Student records with source
students = [
    ('24-00302', 'Mary Joy Debaja', 'BSIT', 3, 'A', 'Local'),
    ('24-00268', 'Jessica Balcena', 'BSIT', 1, 'B', 'Local'),
    ('2026-00125', 'Pedro Reyes', 'BSIT', 2, 'A', 'Local'),
    ('2026-00126', 'Jade Warren Casas', 'BSIT', 3, 'A', 'Local'),
    ('2026-00127', 'Carlo Garcia', 'BSIT', 3, 'A', 'Local'),
    ('2026-00128', 'Sofia Ramos', 'BSIT', 3, 'B', 'Local')
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section, source)
VALUES (?, ?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
print("All student records have source: Local")
