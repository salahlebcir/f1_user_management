#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:33:41 2025

@author: slebcir
"""

#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Message
from app.utils import log_event, token_required
from datetime import datetime

bp = Blueprint('routes', __name__)

ALLOWED_MODES = {
    "tour":      {"need": ["grand_prix","param1"],        "opt": []},
    "comparaison_des_deux_codes_pilotes": {"need": ["grand_prix","param1","param2"], "opt": []},
    "un_seul_code_pilote":  {"need": ["grand_prix","param1"],        "opt": []},
}

def validate_mode(mode):
    return mode in ALLOWED_MODES

def missing_fields(fields):
    return jsonify({"message": f"Missing fields: {', '.join(fields)}"}), 400

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    user = data.get('username')
    pwd  = data.get('password')
    if not user or not pwd:
        return jsonify({"message":"Les champs username et password sont requis"}), 400
    if User.query.filter_by(username=user).first():
        return jsonify({"message":"User exists"}), 400
    u = User(username=user)
    u.set_password(pwd)
    db.session.add(u)
    db.session.commit()
    log_event("register", {"username": user})
    return jsonify({"message":"User registered"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    user = data.get('username')
    pwd  = data.get('password')
    if not user or not pwd:
        return jsonify({"message":"Les champs username et password sont requis"}), 400
    u = User.query.filter_by(username=user).first()
    if not u or not u.verify_password(pwd):
        log_event("failed_login", {"username": user})
        return jsonify({"message":"Invalid credentials"}), 401
    log_event("login", {"username": user})
    return jsonify({"message":"Login successful"}), 200

@bp.route('/messages', methods=['POST'])
@token_required
def post_message(current_user):
    data = request.get_json() or {}
    mode      = data.get('mode')
    grand_prix= data.get('grand_prix')
    p1        = data.get('param1')
    p2        = data.get('param2')

    if not validate_mode(mode):
        return jsonify({"message":"Invalid mode"}), 400

    spec = ALLOWED_MODES[mode]
    missing = [f for f in spec["need"] if not data.get(f)]
    if missing:
        return missing_fields(missing)

    # Créer et enregistrer
    msg = Message(
        mode=mode,
        grand_prix=grand_prix,
        param1=p1,
        param2=p2,
        content=data.get('content'),
        author=current_user
    )
    db.session.add(msg)
    db.session.commit()
    log_event("post_message", {
        "username": current_user.username,
        "mode": mode,
        "grand_prix": grand_prix,
        "param1": p1,
        "param2": p2,
        "content": msg.content
    })
    return jsonify({"message":"Message posted"}), 201

@bp.route('/messages', methods=['GET'])
@token_required
def get_messages(current_user):
    mode       = request.args.get('mode')
    grand_prix = request.args.get('grand_prix')
    p1         = request.args.get('param1')
    p2         = request.args.get('param2')

    if not validate_mode(mode):
        return jsonify({"message":"Invalid mode"}), 400

    spec = ALLOWED_MODES[mode]
    missing = [f for f in spec["need"] if not request.args.get(f)]
    if missing:
        return missing_fields(missing)

    # Construction du filtre
    query = Message.query.filter_by(
        mode=mode,
        grand_prix=grand_prix,
        param1=p1,
        param2=p2 if "param2" in spec["need"] else None
    ).order_by(Message.timestamp.asc())

    result = [{
        "username": m.author.username,
        "content": m.content,
        "timestamp": m.timestamp.isoformat(),
        "mode": m.mode,
        "grand_prix": m.grand_prix,
        "param1": m.param1,
        "param2": m.param2
    } for m in query]
    log_event("get_messages", {
        "username": current_user.username,
        "mode": mode,
        "grand_prix": grand_prix,
        "param1": p1,
        "param2": p2
    })
    return jsonify({"messages": result}), 200
