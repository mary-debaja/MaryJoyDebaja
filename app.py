
import os
import sqlite3
import requests

from datetime import datetime
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATABASE = os.path.join(BASE_DIR, "students.db")

PARTNER_URL = "https://abordaje-jm.onrender.com"


# ==========================================
# DATABASE CONNECTION
# ==========================================

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def initialize_database():
    conn = get_db_connection()

    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                student_id TEXT NOT NULL,
                name TEXT NOT NULL,
                program TEXT NOT NULL,
                year INTEGER NOT NULL,
                section TEXT NOT NULL,
                source TEXT DEFAULT 'Local'
            )
        """)

        columns = [
            row["name"]
            for row in conn.execute(
                "PRAGMA table_info(students)"
            ).fetchall()
        ]

        if "source" not in columns:
            conn.execute("""
                ALTER TABLE students
                ADD COLUMN source TEXT DEFAULT 'Local'
            """)

        conn.commit()

    finally:
        conn.close()


initialize_database()


# ==========================================
# HELPERS
# ==========================================

def validate_student(data):
    if not isinstance(data, dict):
        return None, "Invalid JSON data."

    required = [
        "student_id",
        "name",
        "program",
        "year",
        "section"
    ]

    for field in required:
        if (
            field not in data
            or data[field] is None
            or str(data[field]).strip() == ""
        ):
            return None, f"{field} is required."

    try:
        year = int(data["year"])
    except (ValueError, TypeError):
        return None, "Year must be a number."

    if year not in (1, 2, 3, 4):
        return None, "Year must be between 1 and 4."

    student = {
        "student_id": str(data["student_id"]).strip(),
        "name": str(data["name"]).strip(),
        "program": str(data["program"]).strip(),
        "year": year,
        "section": str(data["section"]).strip()
    }

    return student, None


def get_partner_students():
    response = requests.get(
        PARTNER_URL + "/students",
        timeout=30
    )

    response.raise_for_status()
    data = response.json()

    if not isinstance(data, list):
        raise ValueError(
            "Partner API did not return a student list."
        )

    return data


# ==========================================
# HOME
# ==========================================

@app.route("/")
def home():
    return render_template("index.html")


# ==========================================
# STUDENT INFORMATION
# ==========================================

@app.route("/student")
def get_student():
    return jsonify({
        "student_id": "24-00302",
        "name": "Mary Joy Debaja",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })


# ==========================================
# GREETING
# ==========================================

@app.route("/hello")
def hello():
    name = request.args.get("name", "Student").strip()

    return jsonify({
        "message": f"Hello, {name or 'Student'}!"
    })


# ==========================================
# HOBBY
# ==========================================

@app.route("/hobby")
def hobby():
    return jsonify({
        "student": "Mary Joy Debaja",
        "hobby": "Photography",
        "description": "I enjoy capturing nature and candid moments.",
        "Category": "indoor"
    })


# ==========================================
# AGE CALCULATOR
# ==========================================

@app.route("/age")
def calculate_age():
    year_value = request.args.get("year")

    if not year_value:
        return jsonify({
            "error": "Please provide a birth year."
        }), 400

    try:
        birth_year = int(year_value)
    except ValueError:
        return jsonify({
            "error": "Birth year must be a number."
        }), 400

    current_year = datetime.now().year

    if birth_year < 1900 or birth_year > current_year:
        return jsonify({
            "error": "Invalid birth year."
        }), 400

    return jsonify({
        "birth_year": birth_year,
        "calculated_age": current_year - birth_year
    })


# ==========================================
# READ ALL STUDENTS
# ==========================================

@app.route("/students", methods=["GET"])
def get_students():
    conn = get_db_connection()

    try:
        rows = conn.execute(
            "SELECT * FROM students ORDER BY id DESC"
        ).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


# ==========================================
# READ ONE STUDENT
# ==========================================

@app.route("/students/<int:id>", methods=["GET"])
def get_student_by_id(id):
    conn = get_db_connection()

    try:
        row = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if row is None:
            return jsonify({
                "error": "Student not found"
            }), 404

        return jsonify(dict(row))

    finally:
        conn.close()


# ==========================================
# FILTER BY YEAR
# ==========================================

@app.route("/students/year/<int:year>", methods=["GET"])
def get_students_by_year(year):
    conn = get_db_connection()

    try:
        rows = conn.execute(
            """
            SELECT * FROM students
            WHERE year = ?
            ORDER BY id DESC
            """,
            (year,)
        ).fetchall()

        return jsonify([dict(row) for row in rows])

    finally:
        conn.close()


# ==========================================
# API - READ ALL
# ==========================================

@app.route("/api/students", methods=["GET"])
def api_get_students():
    return get_students()


# ==========================================
# API - CREATE
# STEP 8: RECEIVE EXTERNAL RECORDS
# ==========================================

@app.route("/api/students", methods=["POST"])
def add_student():
    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    # Local form sends "Local".
    # External requests default to "External API".
    source = str(
        data.get("source", "External API")
    ).strip() or "External API"

    conn = get_db_connection()

    try:
        existing = conn.execute(
            """
            SELECT id FROM students
            WHERE student_id = ?
            """,
            (student["student_id"],)
        ).fetchone()

        if existing:
            return jsonify({
                "error": "Student ID already exists."
            }), 409

        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                source
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student added successfully",
            "id": cursor.lastrowid,
            "source": source
        }), 201

    finally:
        conn.close()


# ==========================================
# API - READ ONE
# ==========================================

@app.route("/api/students/<int:id>", methods=["GET"])
def api_get_student(id):
    return get_student_by_id(id)


# ==========================================
# API - UPDATE
# ==========================================

@app.route("/api/students/<int:id>", methods=["PUT"])
def update_student(id):
    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT * FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if existing is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        duplicate = conn.execute(
            """
            SELECT id FROM students
            WHERE student_id = ? AND id != ?
            """,
            (student["student_id"], id)
        ).fetchone()

        if duplicate:
            return jsonify({
                "error": "Student ID already exists."
            }), 409

        conn.execute(
            """
            UPDATE students
            SET student_id = ?,
                name = ?,
                program = ?,
                year = ?,
                section = ?
            WHERE id = ?
            """,
            (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                id
            )
        )

        conn.commit()

        return jsonify({
            "message": "Student updated successfully"
        })

    finally:
        conn.close()


# ==========================================
# API - DELETE
# ==========================================

@app.route("/api/students/<int:id>", methods=["DELETE"])
def delete_student(id):
    conn = get_db_connection()

    try:
        existing = conn.execute(
            "SELECT id FROM students WHERE id = ?",
            (id,)
        ).fetchone()

        if existing is None:
            return jsonify({
                "error": "Student not found."
            }), 404

        conn.execute(
            "DELETE FROM students WHERE id = ?",
            (id,)
        )

        conn.commit()

        return jsonify({
            "message": "Student deleted successfully"
        })

    finally:
        conn.close()


# ==========================================
# CLASSMATE RECORDS
# ==========================================

@app.route("/classmate-records", methods=["GET"])
def classmate_records():
    try:
        return jsonify(get_partner_students())

    except (requests.RequestException, ValueError) as error:
        return jsonify({
            "error": f"Unable to retrieve classmate records: {error}"
        }), 502


# ==========================================
# PARTNER RECORDS
# ==========================================

@app.route("/partner-records", methods=["GET"])
def partner_records():
    try:
        return jsonify(get_partner_students())

    except (requests.RequestException, ValueError) as error:
        return jsonify({
            "error": f"Unable to retrieve partner records: {error}"
        }), 502


# ==========================================
# IMPORT PARTNER STUDENT
# SOURCE MUST BE "IMPORT"
# ==========================================

@app.route("/import-student", methods=["POST"])
def import_student():
    data = request.get_json(silent=True)

    student, error = validate_student(data)

    if error:
        return jsonify({"error": error}), 400

    conn = get_db_connection()

    try:
        existing = conn.execute(
            """
            SELECT id FROM students
            WHERE student_id = ?
            """,
            (student["student_id"],)
        ).fetchone()

        if existing:
            return jsonify({
                "error": "Student ID already exists."
            }), 409

        cursor = conn.execute(
            """
            INSERT INTO students
            (student_id, name, program, year, section, source)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student["student_id"],
                student["name"],
                student["program"],
                student["year"],
                student["section"],
                "IMPORT"
            )
        )

        conn.commit()

        return jsonify({
            "message": "Remote record saved successfully",
            "id": cursor.lastrowid,
            "source": "IMPORT"
        }), 201

    finally:
        conn.close()


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":
    app.run(debug=True)
