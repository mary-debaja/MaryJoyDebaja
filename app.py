
import sqlite3
from datetime import datetime
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
    birth_year = request.args.get('year', type=int)

    if birth_year is None:
        return jsonify({
            "error": "Please provide a valid birth year."
        }), 400

    current_year = datetime.now().year

    if birth_year < 1900 or birth_year > current_year:
        return jsonify({
            "error": "Please enter a valid birth year."
        }), 400

    return jsonify({
        "birth_year": birth_year,
        "calculated_age": current_year - birth_year
    })


# Get All Students
@app.route('/students')
def get_students():
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students ORDER BY id DESC'
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# Get Student by Database ID
@app.route('/students/<int:id>')
def get_student_by_id(id):
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


# Filter Students by Year Level
@app.route('/students/year/<int:year>')
def get_students_by_year(year):
    conn = get_db_connection()

    students = conn.execute(
        'SELECT * FROM students WHERE year = ? ORDER BY id DESC',
        (year,)
    ).fetchall()

    conn.close()

    return jsonify([dict(student) for student in students])


# Add New Student
@app.route('/students/add', methods=['POST'])
def add_student():
    data = request.get_json(silent=True)

    if not isinstance(data, dict):
        return jsonify({
            "error": "Invalid JSON data."
        }), 400

    student_id = str(data.get('student_id') or '').strip()
    name = str(data.get('name') or '').strip()
    program = str(data.get('program') or '').strip()
    section = str(data.get('section') or '').strip()

    try:
        year = int(data.get('year'))
    except (ValueError, TypeError):
        return jsonify({
            "error": "Please select a valid year level."
        }), 400

    if not all([student_id, name, program, section]):
        return jsonify({
            "error": "Please complete all fields."
        }), 400

    if year < 1 or year > 4:
        return jsonify({
            "error": "Year level must be between 1 and 4."
        }), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            'SELECT id FROM students WHERE student_id = ?',
            (student_id,)
        ).fetchone()

        if existing:
            return jsonify({
                "error": "Student ID already exists."
            }), 409

        cursor = conn.execute('''
            INSERT INTO students
            (student_id, name, program, year, section)
            VALUES (?, ?, ?, ?, ?)
        ''', (student_id, name, program, year, section))

        conn.commit()

        return jsonify({
            "message": "Student added successfully!",
            "id": cursor.lastrowid
        }), 201

    finally:
        conn.close()


if __name__ == '__main__':
    app.run(debug=True)
