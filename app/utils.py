#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:32:39 2025

@author: slebcir
"""

import json
from datetime import datetime             # ← ajoutez cette ligne
from flask import current_app, request, jsonify
from functools import wraps
from app.models import User

def log_event(event_type, data):
    """Ajoute une ligne JSON dans le fichier de logs."""
    log_file = current_app.config['LOG_FILE']
    entry = {
        "type": event_type,
        "data": data,
        "time": datetime.utcnow().isoformat()
    }
    try:
        with open(log_file, 'a') as f:
            f.write(json.dumps(entry) + "\n")
    except Exception as e:
        current_app.logger.error(f"Échec écriture log : {e}")


def token_required(f):
    """Vérifie l’Authorization HTTP Basic pour protéger un endpoint."""
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not auth.username or not auth.password:
            return jsonify({"message": "Authentication required"}), 401
        user = User.query.filter_by(username=auth.username).first()
        if not user or not user.verify_password(auth.password):
            log_event("failed_login", {"username": auth.username})
            return jsonify({"message": "Invalid credentials"}), 401
        return f(user, *args, **kwargs)
    return decorated
