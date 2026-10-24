
import sqlite3
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)


# Database Connection
def get_db_connection():
    conn = sqlite3.connect('students.db')
    conn.row_factory = sqlite3.Row
    return conn


# Home Page
@app.route('/')
def home():
    return render_template('index.html')


# Student Information API
@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00302",
        "name": "Mary Joy Debaja",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# Greeting API
@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')

    return jsonify({
        "message": f"Hello, {name}!"
    })


# Hobby API
@app.route('/hobby')
def hobby():
    return jsonify({
        "student": "Mary Joy Debaja",
        "hobby": "Photography",
        "description": "I love capturing nature and candid moments.",
        "Category": "indoor"
    })


# Age Calculator API
@app.route('/age')
def calculate_age():
    try:
        birth_year = request.args.get('year', type=int)

        if not birth_year:
            return jsonify({
                "error": "Please provide a birth year, e.g., /age?year=2003"
            })

        current_year = 2026
        age = current_year - birth_year

        return jsonify({
            "birth_year": birth_year,
            "calculated_age": age
        })

    except Exception as e:
        return jsonify({"error": str(e)})


# Get All Students from Database
@app.route('/students')
def get_students():
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# Get Student by ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({"error": "Student not found"}), 404

    return jsonify(dict(student))


# Additional Task: Filter Students by Year Level
@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE year = ?', (year,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# ==========================================
# CREATE - Add New Student
# ==========================================
@app.route('/api/students', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data"
        }), 400

    required = ['student_id', 'name', 'program', 'year', 'section']

    if any(
        field not in data or data[field] is None
        or str(data[field]).strip() == ''
        for field in required
    ):
        return jsonify({
            "error": "Please complete all fields"
        }), 400

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid year level"
        }), 400

    if year not in (1, 2, 3, 4):
        return jsonify({
            "error": "Year must be between 1 and 4"
        }), 400

    student_id = str(data['student_id']).strip()
    name = str(data['name']).strip()
    program = str(data['program']).strip()
    section = str(data['section']).strip()

    conn = get_db_connection()

    try:
        existing = conn.execute(
            'SELECT id FROM students WHERE student_id = ?',
            (student_id,)
        ).fetchone()

        if existing:
            return jsonify({
                "error": "Student ID already exists"
            }), 409

        cursor = conn.execute(
            """INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)""",
            (student_id, name, program, year, section)
        )

        conn.commit()
        new_id = cursor.lastrowid

        return jsonify({
            "message": "Student added",
            "id": new_id
        }), 201

    finally:
        conn.close()


# ==========================================
# READ - Get Student by ID
# ==========================================
@app.route('/api/students/<int:id>', methods=['GET'])
def api_get_student(id):
    conn = get_db_connection()

    student = conn.execute(
        'SELECT * FROM students WHERE id = ?', (id,)
    ).fetchone()

    conn.close()

    if student is None:
        return jsonify({
            "error": "Student not found"
        }), 404

    return jsonify(dict(student))


# ==========================================
# UPDATE - Update Existing Student
# ==========================================
@app.route('/api/students/<int:id>', methods=['PUT'])
def update_student(id):
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data"
        }), 400

    required = ['student_id', 'name', 'program', 'year', 'section']

    if any(
        field not in data or data[field] is None
        or str(data[field]).strip() == ''
        for field in required
    ):
        return jsonify({
            "error": "Please complete all fields"
        }), 400

    try:
        year = int(data['year'])
    except (ValueError, TypeError):
        return jsonify({
            "error": "Invalid year level"
        }), 400

    if year not in (1, 2, 3, 4):
        return jsonify({
            "error": "Year must be between 1 and 4"
        }), 400

    student_id = str(data['student_id']).strip()
    name = str(data['name']).strip()
    program = str(data['program']).strip()
    section = str(data['section']).strip()

    conn = get_db_connection()

    try:
        student = conn.execute(
            'SELECT * FROM students WHERE id = ?',
            (id,)
        ).fetchone()

        if student is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        duplicate = conn.execute(
            'SELECT id FROM students WHERE student_id = ? AND id != ?',
            (student_id, id)
        ).fetchone()

        if duplicate:
            return jsonify({
                "error": "Student ID already exists"
            }), 409

        conn.execute(
            """UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?""",
            (student_id, name, program, year, section, id)
        )

        conn.commit()

        return jsonify({
            "message": "Student updated"
        }), 200

    finally:
        conn.close()


# ==========================================
# DELETE - Delete Student
# ==========================================
@app.route('/api/students/<int:id>', methods=['DELETE'])
def delete_student(id):
    conn = get_db_connection()

    try:
        cursor = conn.execute(
            'DELETE FROM students WHERE id = ?',
            (id,)
        )

        if cursor.rowcount == 0:
            return jsonify({
                "error": "Student not found"
            }), 404

        conn.commit()

        return jsonify({
            "message": "Student deleted"
        }), 200

    finally:
        conn.close()

# READ - Get All Students (For Classmate)
@app.route('/api/students', methods=['GET'])
def api_students():
    conn = get_db_connection()

    rows = conn.execute(
        'SELECT * FROM students'
    ).fetchall()

    conn.close()

    return jsonify([dict(row) for row in rows])


if __name__ == '__main__':
    app.run(debug=True)
