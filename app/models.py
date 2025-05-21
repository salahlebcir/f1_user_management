#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 21 21:32:22 2025

@author: slebcir
"""

from datetime import datetime
from flask import current_app
from app import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    messages = db.relationship('Message', backref='author', lazy='dynamic')
    # … (mêmes méthodes set_password, verify_password)

class Message(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    mode = db.Column(db.String(64), nullable=False)
    grand_prix = db.Column(db.String(128), nullable=False)
    param1 = db.Column(db.String(64), nullable=False)   # tourNum ou pilote1
    param2 = db.Column(db.String(64), nullable=True)    # pilote2 pour comparaison
    content = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    def __repr__(self):
        base = f"<Msg[{self.mode}|{self.grand_prix}|{self.param1}"
        if self.param2:
            base += f", {self.param2}"
        return base + f"] {self.content[:20]}>"


