
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
    section TEXT NOT NULL
)
''')

cursor.execute("DELETE FROM students")

students = [
    ('24-00302', 'Mary Joy Debaja', 'BSIT', 3, 'A'),
    ('24-00268', 'Jessica Balcena', 'BSIT', 1, 'B'),
    ('2026-00125', 'Pedro Reyes', 'BSIT', 2, 'A'),
    ('2026-00126', 'Jade Warren Casas', 'BSIT', 3, 'A'),
    ('2026-00127', 'Carlo Garcia', 'BSIT', 3, 'A'),
    ('2026-00128', 'Sofia Ramos', 'BSIT', 3, 'B')
]

cursor.executemany('''
INSERT INTO students (student_id, name, program, year, section)
VALUES (?, ?, ?, ?, ?)
''', students)

conn.commit()
conn.close()

print("Database created successfully.")
