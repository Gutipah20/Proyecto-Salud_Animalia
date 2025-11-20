from . import app
from flask import render_template

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/admin")
def admin():
    return render_template("admin.html")

@app.get("/cita")
def cita():
    return render_template("cita.html")


@app.get("/contacto")
def contacto():
    return render_template("contacto.html")


@app.get("/login")
def login():
    return render_template("login.html")


@app.get("/nosotros")
def nosotros():
    return render_template("nosotros.html")


@app.get("/registro")
def registro():
    return render_template("registro.html")


@app.get("/servicios")
def servicios():
    return render_template("servicios.html")
