#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:33:41 2025

@author: slebcir
"""


from flask import Blueprint, request, jsonify
from app import db
from app.models import User, Message
from app.utils import log_event, token_required
from datetime import datetime

bp = Blueprint('routes', __name__)

ALLOWED_MODES = [
    "tour",
    "comparaison_des_deux_codes_pilotes",
    "un_seul_code_pilote"
]

def validate_mode(mode):
    return mode in ALLOWED_MODES

@bp.route('/register', methods=['POST'])
def register():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message": "Les champs username et password sont requis"}), 400
    if User.query.filter_by(username=username).first():
        return jsonify({"message": "User exists"}), 400
    user = User(username=username)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    log_event("register", {"username": username})
    return jsonify({"message": "User registered"}), 201

@bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    username = data.get('username')
    password = data.get('password')
    if not username or not password:
        return jsonify({"message": "Les champs username et password sont requis"}), 400
    user = User.query.filter_by(username=username).first()
    if not user or not user.verify_password(password):
        log_event("failed_login", {"username": username})
        return jsonify({"message": "Invalid credentials"}), 401
    log_event("login", {"username": username})
    return jsonify({"message": "Login successful"}), 200

@bp.route('/messages', methods=['POST'])
@token_required
def post_message(current_user):
    data = request.get_json() or {}
    content = data.get('content')
    mode = data.get('mode')
    if not content or not mode:
        return jsonify({"message": "Missing fields"}), 400
    if not validate_mode(mode):
        return jsonify({"message": "Invalid mode"}), 400
    msg = Message(content=content, author=current_user)
    db.session.add(msg)
    db.session.commit()
    log_event("post_message", {
        "username": current_user.username,
        "mode": mode,
        "content": content
    })
    return jsonify({"message": "Message posted"}), 201

@bp.route('/messages', methods=['GET'])
@token_required
def get_messages(current_user):
    mode = request.args.get('mode')
    if not mode:
        return jsonify({"message": "Mode required"}), 400
    if not validate_mode(mode):
        return jsonify({"message": "Invalid mode"}), 400
    msgs = Message.query.order_by(Message.timestamp.asc()).all()
    result = [{
        "username": m.author.username,
        "content": m.content,
        "timestamp": m.timestamp.isoformat()
    } for m in msgs]
    log_event("get_messages", {
        "username": current_user.username,
        "mode": mode
    })
    return jsonify({"messages": result}), 200
