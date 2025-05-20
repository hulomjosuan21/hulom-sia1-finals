import os
from flask import Flask, make_response, jsonify
from flask_cors import CORS
from src.config import Config
from src.register_routes import register_routes
from src.extensions import db, migrate, jwt, bcrypt, limiter
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

def __initialize__() -> Flask:
    app = Flask(__name__)

    app.config.from_object(Config)

    CORS(app, 
         supports_credentials=app.config['CORS_SUPPORT_CREDENTIALS'],
         origins=app.config['CORS_ORIGINS']
    )
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)
    bcrypt.init_app(app)
    limiter.init_app(app)
    app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'uploads')

    with app.app_context():
        db.create_all()
        register_routes(app)

    return app
