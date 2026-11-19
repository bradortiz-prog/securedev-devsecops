import sqlite3
from flask import Flask, request, render_template_string

app = Flask(__name__)
# Vulnerabilidad 1: Clave secreta hardcodeada
app.config['SECRET_KEY'] = 'super_secreto_12345'

def init_db():
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, username TEXT, password TEXT)')
    c.execute("INSERT OR IGNORE INTO users (id, username, password) VALUES (1, 'admin', 'admin123')")
    conn.commit()
    conn.close()

@app.route('/')
def index():
    # Vulnerabilidad 2: XSS Reflejado sin sanitización
    nombre = request.args.get('nombre', 'Invitado')
    template = f"""
    <html>
        <head><title>SecureDev Portal</title></head>
        <body>
            <h1>Bienvenido a SecureDev, {nombre}</h1>
            <form action="/login" method="POST">
                Usuario: <input type="text" name="username"><br>
                Clave: <input type="password" name="password"><br>
                <input type="submit" value="Ingresar">
            </form>
        </body>
    </html>
    """
    return render_template_string(template)

@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username', '')
    password = request.form.get('password', '')
    conn = sqlite3.connect('usuarios.db')
    c = conn.cursor()
    # Vulnerabilidad 3: SQL Injection por concatenación directa
    query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
    c.execute(query)
    user = c.fetchone()
    conn.close()
    if user:
        return f"Acceso concedido para {user[1]}"
    return "Credenciales inválidas", 401

if __name__ == '__main__':
    init_db()
    # Vulnerabilidad 4: Modo debug activo y sin cabeceras HTTP de seguridad
    app.run(host='0.0.0.0', port=5000, debug=True)