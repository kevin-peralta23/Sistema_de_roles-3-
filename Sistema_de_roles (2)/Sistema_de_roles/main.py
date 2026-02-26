# Importamos las librerías necesarias de Flask
from flask import Flask, render_template, request, redirect, session, abort
from functools import wraps

# Librerías para generar contraseñas automáticas
import random
import string

# Librería para hash seguro de contraseñas
from werkzeug.security import generate_password_hash, check_password_hash

# Creamos la aplicación Flask
app = Flask(__name__)

# Clave secreta para manejar sesiones (login)
app.secret_key = "holabuenastardes"

# Configuración segura de cookies (A02)
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'

# ROLES DEL SISTEMA

# Lista de roles disponibles en el sistema
roles = ["Administrador", "Maestro", "Alumno"]

# ADMIN POR DEFECTO

# Lista donde se guardan los usuarios del sistema
usuarios = [
    {
        "usuario": "admin",  
        "password": generate_password_hash("guadalupe21_p"),  # Contraseña hasheada
        "rol": "Administrador"
    }
]

# DECORADORES DE SEGURIDAD

# Verifica que haya sesión activa
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario" not in session:
            return redirect("/")
        return f(*args, **kwargs)
    return decorated_function

# Verifica que el usuario tenga el rol correcto
def role_required(rol):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "rol" not in session or session["rol"] != rol:
                abort(403)  # Prohibido
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

# FUNCION CONTRASEÑA AUTOMATICA

# Función que genera una contraseña aleatoria
def generar_password(longitud=8):
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choice(caracteres) for _ in range(longitud))

# LOGIN

# Ruta principal (login)
@app.route("/", methods=["GET", "POST"])
def login():
    
    if request.method == "POST":
        usuario = request.form["usuario"]
        password = request.form["password"]

        for u in usuarios:
            if u["usuario"] == usuario and check_password_hash(u["password"], password):

                # Prevención de fijación de sesión
                session.clear()

                session["usuario"] = usuario
                session["rol"] = u["rol"]

                if u["rol"] == "Administrador":
                    return redirect("/admin")
                elif u["rol"] == "Maestro":
                    return redirect("/maestro")
                elif u["rol"] == "Alumno":
                    return redirect("/alumno")
                else:
                    return redirect("/panel")

        return render_template("login.html", error="Usuario o contraseña incorrecta")

    return render_template("login.html")

# PANEL ADMIN

@app.route("/admin")
@login_required
@role_required("Administrador")
def admin():
    return render_template("admin.html", usuarios=usuarios, roles=roles)

# CREAR USUARIO

@app.route("/crear_usuario", methods=["GET", "POST"])
@login_required
@role_required("Administrador")
def crear_usuario():

    if request.method == "POST":
        nuevo_usuario = request.form["usuario"]
        rol = request.form["rol"]

        # Validar que el rol exista (A04)
        if rol not in roles:
            abort(400)

        # Generar contraseña automática
        password_generada = generar_password()

        usuarios.append({
            "usuario": nuevo_usuario,
            "password": generate_password_hash(password_generada),
            "rol": rol
        })

        return render_template("usuario_creado.html",
                               usuario=nuevo_usuario,
                               password=password_generada,
                               rol=rol)

    return render_template("crear_usuario.html", roles=roles)

# CREAR ROL NUEVO

@app.route("/crear_rol", methods=["GET", "POST"])
@login_required
@role_required("Administrador")
def crear_rol():

    if request.method == "POST":
        nuevo_rol = request.form["rol"]

        # Validar que no sea vacío y no exista
        if nuevo_rol and nuevo_rol not in roles:
            roles.append(nuevo_rol)

        return redirect("/admin")

    return render_template("crear_rol.html")

# PANEL MAESTRO

@app.route("/maestro")
@login_required
@role_required("Maestro")
def maestro():
    return render_template("maestro.html")

# PANEL ALUMNO

@app.route("/alumno")
@login_required
@role_required("Alumno")
def alumno():
    return render_template("alumno.html")

# ROLES NUEVOS

@app.route("/panel")
@login_required
def panel():
    return render_template("panel.html")

# LOGOUT

@app.route("/logout")
@login_required
def logout():
    session.clear()
    return redirect("/")

# EJECUTAR APP

if __name__ == "__main__":
    app.run(debug=False)  # debug desactivado en producción