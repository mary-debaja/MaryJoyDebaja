from flask import Flask, jsonify, request

app = Flask(__name__)

@app.route('/')
def home():
    return "Welcome to Mary's API!"

@app.route('/student')
def get_student():
    return jsonify({
        "student_id": "24-00302",
        "name": "Mary Joy Debaja",
        "program": "BSIT",
        "year": 3,
        "section": "A"
    })

@app.route('/hello')
def say_hello():
    name = request.args.get('name', 'Student')
    return jsonify({
        "message": f"Hello, {name}!"
    })

# 🔹 New Endpoint 1: Hobby (static data)
@app.route('/hobby')
def hobby():
    return jsonify({
        "student": "Mary Joy Debaja",
        "hobby": "Photography",
        "description": "I love capturing nature and candid moments."
        "Category": "indoor"
    })

# 🔹 New Endpoint 2: Age Calculator (accepts input from URL)
@app.route('/age')
def calculate_age():
    try:
        birth_year = request.args.get('year', type=int)
        if not birth_year:
            return jsonify({"error": "Please provide a birth year in the URL, e.g., /age?year=2003"})
        
        current_year = 2026
        age = current_year - birth_year
        return jsonify({
            "birth_year": birth_year,
            "calculated_age": age
        })
    except Exception as e:
        return jsonify({"error": str(e)})

if __name__ == '__main__':
    app.run(debug=True)
