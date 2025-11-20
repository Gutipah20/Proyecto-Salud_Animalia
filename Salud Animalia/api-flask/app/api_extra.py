from flask import request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from .models import User, Reserva, UserRole
from .db_init import db
from . import app


def ok(data=None, code=200):
    payload = {"ok": True}
    if isinstance(data, dict): 
        payload.update(data)
    elif data is not None: 
        payload["data"] = data
    return jsonify(payload), code


def err(msg, code=400):
    return jsonify({"ok": False, "error": msg}), code


@app.post("/api/register")
def register_user():
    data = request.get_json(force=True)
    name = data.get("name")
    email = data.get("email")
    password = data.get("password")
    
    if not all([name, email, password]): 
        return err("Faltan datos: name, email, password")
    
    if User.query.filter_by(email=email).first():
        return err("El correo ya está registrado")
    
    u = User(
        name=name, 
        email=email, 
        password=generate_password_hash(password), 
        role=UserRole.USER
    )
    db.session.add(u)
    db.session.commit()
    return ok({"message": "Usuario registrado con éxito"}, 201)


@app.post("/api/login")
def login_user():
    data = request.get_json(force=True)
    email = data.get("email")
    password = data.get("password")
    
    u = User.query.filter_by(email=email).first()
    if not u or not check_password_hash(u.password, password):
        return err("Credenciales incorrectas", 401)
    
    return ok({
        "user": {
            "id": u.id,
            "name": u.name,
            "email": u.email,
            "role": u.role.value
        }
    })


@app.get("/api/users")
def list_users():
    users = User.query.all()
    data = [{"id": u.id, "name": u.name, "email": u.email, "role": u.role.value} for u in users]
    return ok({"users": data})


@app.post("/api/reservas")
def crear_reserva():
    data = request.get_json(force=True)
    user_id = data.get("user_id")
    mascota = data.get("mascota")
    motivo = data.get("motivo")
    fecha_str = data.get("fecha")
    
    if not all([user_id, mascota, motivo, fecha_str]):
        return err("Datos incompletos: user_id, mascota, motivo, fecha")

    try:
        fecha_dt = datetime.fromisoformat(fecha_str)
    except Exception:
        return err("Formato de fecha inválido. Use ISO: YYYY-MM-DDTHH:MM:SS")

    u = User.query.get(user_id)
    if not u:
        return err("Usuario no encontrado", 404)
    
    r = Reserva(user_id=user_id, mascota=mascota, motivo=motivo, fecha=fecha_dt)
    db.session.add(r)
    db.session.commit()
    return ok({"message": "Reserva creada con éxito", "id": r.id}, 201)


@app.get("/api/reservas")
def listar_reservas():
    user_id = request.args.get("user_id", type=int)
    q = Reserva.query.order_by(Reserva.fecha.desc())
    
    if user_id:
        q = q.filter(Reserva.user_id == user_id)
    
    data = [r.to_dict() for r in q.all()]
    return ok({"reservas": data})


@app.get("/api/reservas/admin")
def listar_todas_reservas():
    reservas = Reserva.query.order_by(Reserva.fecha.desc()).all()
    data = [r.to_dict() for r in reservas]
    return ok({"reservas": data})


@app.delete("/api/reservas/<int:reserva_id>")
def eliminar_reserva(reserva_id):
    r = Reserva.query.get(reserva_id)
    if not r:
        return err("Reserva no encontrada", 404)
    
    db.session.delete(r)
    db.session.commit()
    return ok({"message": "Reserva eliminada"})

@app.get("/api/reservas/<int:reserva_id>")
def obtener_reserva(reserva_id):
    r = Reserva.query.get(reserva_id)
    if not r:
        return err("Reserva no encontrada", 404)
    return ok({"reserva": r.to_dict()})


@app.put("/api/reservas/<int:reserva_id>")
def actualizar_reserva(reserva_id):
    r = Reserva.query.get(reserva_id)
    if not r:
        return err("Reserva no encontrada", 404)
    
    data = request.get_json(force=True)
    mascota = data.get("mascota")
    motivo = data.get("motivo")
    fecha_str = data.get("fecha")
    
    if mascota:
        r.mascota = mascota
    if motivo:
        r.motivo = motivo
    if fecha_str:
        try:
            r.fecha = datetime.fromisoformat(fecha_str)
        except Exception:
            return err("Formato de fecha inválido")
    
    db.session.commit()
    return ok({"message": "Reserva actualizada con éxito", "reserva": r.to_dict()})
