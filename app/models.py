#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:32:22 2025

@author: slebcir
"""

# app/models.py
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    messages = db.relationship('Message', backref='author', lazy='dynamic')

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f"<User {self.username}>"

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(64), nullable=False)
    grand_prix = db.Column(db.String(128), nullable=False)
    param1 = db.Column(db.String(64), nullable=False)
    param2 = db.Column(db.String(64), nullable=True)
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        base = f"<Msg[{self.mode}|{self.grand_prix}|{self.param1}"
        if self.param2:
            base += f", {self.param2}"
        return base + f"] {self.content[:20]}>"
