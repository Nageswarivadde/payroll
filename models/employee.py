from . import db

class Employee(db.Model):
    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    position = db.Column(db.String(100), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    salary = db.Column(db.Float, nullable=False)
    tax = db.Column(db.Float, nullable=True)
    benefits = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Employee {self.name} - {self.position}>'
