from flask import Blueprint, render_template, request, flash
from models.employee import Employee

payroll_bp = Blueprint('payroll', __name__)

@payroll_bp.route('/generate-payslip', methods=['GET', 'POST'])
def generate_payslip():
    employees = Employee.query.all()
    message = None

    if request.method == 'POST':
        emp_id = int(request.form['employee_id'])
        emp = Employee.query.get(emp_id)
        if emp:
            tax = emp.salary * 0.1  # 10% tax
            benefits = emp.salary * 0.05  # 5% benefits
            net_pay = emp.salary - tax + benefits
            period = 'May 2025'  # Example period

            # You can implement saving payslip to DB here if you want

            message = f"Payslip generated for {emp.name}."
        else:
            message = 'Employee not found.'

    return render_template('generate_payslip.html', employees=employees, message=message)
@payroll_bp.route('/view-payslip')
def view_payslip():
    return render_template('view_payslip.html')

