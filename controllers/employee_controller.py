from flask import Blueprint, render_template, request, redirect, url_for, flash
from models.employee import Employee
from models import db

employee_bp = Blueprint('employee', __name__)

@employee_bp.route('/add-employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        salary = float(request.form['salary'])
        department = request.form['department']

        if Employee.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('employee.add_employee'))

        employee = Employee(name=name, email=email, position=position, salary=salary, department=department)
        db.session.add(employee)
        db.session.commit()
        flash('Employee added successfully!')
        return redirect(url_for('employee.employee_list'))

    return render_template('add_employee.html')

@employee_bp.route('/employees')
def employee_list():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)

@employee_bp.route('/edit-employee/<int:id>', methods=['GET', 'POST'])
def edit_employee(id):
    employee = Employee.query.get_or_404(id)
    if request.method == 'POST':
        employee.name = request.form['name']
        employee.email = request.form['email']
        employee.position = request.form['position']
        employee.salary = float(request.form['salary'])
        employee.department = request.form['department']

        db.session.commit()
        flash('Employee updated successfully!')
        return redirect(url_for('employee.employee_list'))

    return render_template('edit_employee.html', employee=employee)

@employee_bp.route('/delete-employee/<int:id>')
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!')
    return redirect(url_for('employee.employee_list'))
