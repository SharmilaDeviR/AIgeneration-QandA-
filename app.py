from flask import Flask, request, render_template
import sqlite3
import random

# Initialize the Flask app
app = Flask(__name__)

# Connect to SQLite database
def get_db_connection():
    conn = sqlite3.connect('education_system.db')
    conn.row_factory = sqlite3.Row
    return conn

# Create tables if not exist
def init_db():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS CourseMaterials (
            id INTEGER PRIMARY KEY,
            staff_id TEXT,
            material TEXT
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS Questions (
            id INTEGER PRIMARY KEY,
            material_id INTEGER,
            question TEXT,
            FOREIGN KEY (material_id) REFERENCES CourseMaterials (id)
        )
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS StudentResponses (
            id INTEGER PRIMARY KEY,
            question_id INTEGER,
            student_id TEXT,
            response TEXT,
            is_correct BOOLEAN,
            FOREIGN KEY (question_id) REFERENCES Questions (id)
        )
        ''')
        conn.commit()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/upload', methods=['GET', 'POST'])
def upload_material():
    if request.method == 'POST':
        staff_id = request.form['staff_id']
        material = request.form['material']
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO CourseMaterials (staff_id, material) VALUES (?, ?)', (staff_id, material))
            conn.commit()
        return 'Material uploaded successfully!'
    return render_template('upload.html')

def generate_question(material):
    sentences = material.split('.')
    return random.choice(sentences).strip() + '?'

@app.route('/generate_questions', methods=['POST'])
def generate_questions():
    material_id = request.form['material_id']
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT material FROM CourseMaterials WHERE id = ?', (material_id,))
        material = cursor.fetchone()
        
        if material:
            question = generate_question(material['material'])
            cursor.execute('INSERT INTO Questions (material_id, question) VALUES (?, ?)', (material_id, question))
            conn.commit()
            return f'Question generated: {question}'
    return 'Material not found.'

@app.route('/send_question/<student_id>', methods=['GET'])
def send_question(student_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT question FROM Questions ORDER BY RANDOM() LIMIT 1')
        question = cursor.fetchone()
        
        if question:
            return f'Sent question to {student_id}: {question[0]}'
    return 'No questions available.'

@app.route('/submit_answer', methods=['POST'])
def submit_answer():
    question_id = request.form['question_id']
    student_id = request.form['student_id']
    response = request.form['response']
    
    # Placeholder for answer verification logic
    is_correct = True  # Replace with actual logic
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO StudentResponses (question_id, student_id, response, is_correct) VALUES (?, ?, ?, ?)',
                       (question_id, student_id, response, is_correct))
        conn.commit()
    return 'Response submitted successfully!'

if __name__ == '__main__':
    init_db()
    app.run(debug=True)
