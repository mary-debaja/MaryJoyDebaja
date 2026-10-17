
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


if __name__ == '__main__':
    app.run(debug=True)
