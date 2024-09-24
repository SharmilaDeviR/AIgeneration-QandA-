import sqlite3
import random
import gradio as gr

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

# Function to upload course material
def upload_material(staff_id, material):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO CourseMaterials (staff_id, material) VALUES (?, ?)', (staff_id, material))
        conn.commit()
    return "Material uploaded successfully!"

# Function to generate a question from the material
def generate_question(material):
    sentences = material.split('.')
    return random.choice(sentences).strip() + '?'

# Function to generate questions based on material ID
def generate_questions(material_id):
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

# Function to send a question to a student
def send_question(student_id):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT question FROM Questions ORDER BY RANDOM() LIMIT 1')
        question = cursor.fetchone()
        
        if question:
            return f'Sent question to {student_id}: {question[0]}'
    return 'No questions available.'

# Function to submit an answer
def submit_answer(question_id, student_id, response):
    # Placeholder for answer verification logic
    is_correct = True  # Replace with actual logic
    
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute('INSERT INTO StudentResponses (question_id, student_id, response, is_correct) VALUES (?, ?, ?, ?)',
                       (question_id, student_id, response, is_correct))
        conn.commit()
    return 'Response submitted successfully!'

# Initialize the database
init_db()

# Create Gradio interfaces
upload_interface = gr.Interface(
    fn=upload_material,
    inputs=[gr.Textbox(label="Staff ID"), gr.Textbox(label="Material")],
    outputs="text",
    title="Upload Course Material"
)

generate_interface = gr.Interface(
    fn=generate_questions,
    inputs=gr.Textbox(label="Material ID"),
    outputs="text",
    title="Generate Question"
)

send_interface = gr.Interface(
    fn=send_question,
    inputs=gr.Textbox(label="Student ID"),
    outputs="text",
    title="Send Question to Student"
)

submit_interface = gr.Interface(
    fn=submit_answer,
    inputs=[
        gr.Textbox(label="Question ID"),
        gr.Textbox(label="Student ID"),
        gr.Textbox(label="Response")
    ],
    outputs="text",
    title="Submit Answer"
)

# Launch the Gradio app
if __name__ == "__main__":
    gr.TabbedInterface([upload_interface, generate_interface, send_interface, submit_interface]).launch()
