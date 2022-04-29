from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///printer.db'
# app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:12345@192.168.1.46:5432/PrinterBD"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

class MOL(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fio = db.Column(db.String(50), nullable=True)
    department = db.Column(db.String(100))

    def __repr__(self):
        return f"<MOL {self.id}>"

class Device(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=True)
    inv = db.Column(db.String(50))
    sn = db.Column(db.String(100), unique=True)
    kab = db.Column(db.Integer, nullable=True)
    data_vvoda = db.Column(db.DateTime)
    molid = db.Column(db.Integer, db.ForeignKey('MOL.id'))

    def __repr__(self):
        return f"<Device {self.id}>"

class Job(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, default=datetime.utcnow)
    type_work = db.Column(db.String(300), nullable=True)
    note = db.Column(db.String(300))
    deviceid = db.Column(db.Integer, db.ForeignKey('device.id'))

    def __repr__(self):
        return f"<Job {self.id}>"

if __name__ == '__main__':
    app.run(debug=True)