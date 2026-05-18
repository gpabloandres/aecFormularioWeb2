# -*- coding: utf-8 -*-
import os
import sqlite3
import csv
import io
from datetime import datetime
from flask import Flask, request, g, redirect, url_for, Response, render_template

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
DATABASE = os.path.join(basedir, 'respuestas_docentes.db')

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        cursor = db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS respuestas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha TEXT NOT NULL,
                nombre TEXT,
                cargo TEXT,
                comentario_relaciones TEXT,
                comentario_cuidado TEXT,
                comentario_sanciones TEXT,
                comentario_aplicacion TEXT,
                sugerencias_generales TEXT
            )
        ''')
        db.commit()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    nombre = request.form.get('nombre')
    cargo = request.form.get('cargo')
    comentario_relaciones = request.form.get('comentario_relaciones', '')
    comentario_cuidado = request.form.get('comentario_cuidado', '')
    comentario_sanciones = request.form.get('comentario_sanciones', '')
    comentario_aplicacion = request.form.get('comentario_aplicacion', '')
    sugerencias_generales = request.form.get('sugerencias_generales', '')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('''
        INSERT INTO respuestas (fecha, nombre, cargo, comentario_relaciones, comentario_cuidado, comentario_sanciones, comentario_aplicacion, sugerencias_generales)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        nombre,
        cargo,
        comentario_relaciones,
        comentario_cuidado,
        comentario_sanciones,
        comentario_aplicacion,
        sugerencias_generales
    ))
    db.commit()
    return redirect(url_for('thank_you'))

@app.route('/thank-you')
def thank_you():
    return """
    <div style='font-family: sans-serif; text-align: center; padding-top: 50px;'>
        <h1>¡Gracias por tu participación, colega!</h1>
        <p>Tus aportes han sido enviados correctamente.</p>
        <a href='/'>Volver al formulario</a>
    </div>
    """

@app.route('/download')
def download_data():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM respuestas')
    data = cursor.fetchall()
    
    csv_output = io.StringIO()
    writer = csv.writer(csv_output)
    
    headers = [description[0] for description in cursor.description]
    writer.writerow(headers)
    writer.writerows(data)
    
    response = Response(csv_output.getvalue(), mimetype='text/csv')
    response.headers['Content-Disposition'] = 'attachment;filename=respuestas_docentes.csv'
    return response

# Call init_db() here so it runs when PythonAnywhere imports the app
with app.app_context():
    init_db()

if __name__ == '__main__':
    app.run(port=5002, debug=True)
