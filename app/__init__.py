#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:31:19 2025

@author: slebcir
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from config import Config

db = SQLAlchemy()

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialisation des extensions
    db.init_app(app)
    CORS(app)

    # Enregistrement des routes
    from app.routes import bp as routes_bp
    app.register_blueprint(routes_bp)

    # Création automatique des tables
    with app.app_context():
        db.create_all()

    return app
