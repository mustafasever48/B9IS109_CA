from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Technician(db.Model):
    __tablename__ = 'Technician'
    Technician_ID = db.Column(db.Integer, primary_key=True)
    Tech_Name = db.Column(db.String(255))
    Tech_Qual = db.Column(db.String(255))
    Tech_Tiitle = db.Column(db.String(255))
    Tech_Email = db.Column(db.String(255), unique=True)
    Pass = db.Column(db.String(255))