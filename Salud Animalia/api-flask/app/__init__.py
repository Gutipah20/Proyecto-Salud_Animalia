from flask import Flask
from flask_cors import CORS
from .db_init import db, ma, configure_db

app = Flask(
    __name__,
    template_folder="/app/templates", 
    static_folder="/app/static",        
    static_url_path="/static"        
)

CORS(app, resources={r"/api/*": {"origins": "*"}})

configure_db(app)

app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

from . import models

with app.app_context():
    db.create_all()
    
    from werkzeug.security import generate_password_hash
    from .models import User, UserRole
    
    admin = User.query.filter_by(email="admin@veterinaria.com").first()
    if not admin:
        admin = User(
            name="Administrador",
            email="admin@veterinaria.com",
            password=generate_password_hash("123456"),
            role=UserRole.ADMIN
        )
        db.session.add(admin)
        db.session.commit()
        print("[SEED] Admin creado: admin@veterinaria.com")

from . import routes
from . import api_extra
