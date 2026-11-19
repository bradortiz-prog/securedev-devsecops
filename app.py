import os
import sqlite3
from flask import Flask, request, render_template_string
from markupsafe import escape

app = Flask(__name__)
# Mitigación 1: Obtener SECRET_KEY desde variable de entorno con respaldo seguro
app.config['SECRET_KEY'] = os.environ.get('FLASK_SECRET_KEY', os.urandom(24))

def init_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()

# Mitigación adicional: Cabeceras de seguridad HTTP (CSP, X-Frame-Options, X-Content-Type-Options)
@app.after_request
def add_security_headers(response):
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Content-Security-Policy'] = "default-src 'self'"
    return response

@app.route('/')
def index():
    # Mitigación 2: Sanitización / escape de entrada para prevenir XSS Reflejado
    nombre = escape(request.args.get('nombre', 'Invitado'))
    template = """
    <html>
        <head><title>SecureDev Portal</title></head>
        <body>
            <h1>Bienvenido a SecureDev, {{ nombre }}</h1>
            <form action="/login" method="POST">
                Usuario: <input type="text" name="username"><br>
                Clave: <input type="password" name="password"><br>
                <input type="submit" value="Ingresar">
            </form>
        </body>
    </html>
    """
    return render_template_string(template, nombre=nombre)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    # Mitigación 3: Consultas parametrizadas (Prepared Statements) contra SQL Injection
    query = "SELECT * FROM users WHERE username = ? AND password = ?"
    c.execute(query, (username, password))
    user = c.fetchone()
    conn.close()
    if user:
        return f"Acceso concedido para {escape(user[1])}"
    return "Credenciales inválidas", 401

if __name__ == '__main__':
    init_db()
    # Mitigación 4: Modo debug desactivado para entorno de producción
    app.run(host='0.0.0.0', port=5000, debug=False)