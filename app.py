from flask import Flask, render_template, request, redirect, url_for, flash, send_file, session
from models import db
from models.employee import Employee
import io
from flask_pymongo import PyMongo
from controllers.auth_controller import auth_bp
from controllers.employee_controller import employee_bp
from controllers.payroll_controller import payroll_bp
from utils.pdf_generator import generate_payslip_pdf
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'nageswari1234'

# MongoDB Configuration (must include a valid database name!)
app.config["MONGO_URI"] = "mongodb+srv://nageswarivadde2:Nageswari%40098@cluster0.zaxcx89.mongodb.net/payroll"

mongo = PyMongo(app)
if not mongo.db:
    raise Exception("MongoDB not connected properly. Check MONGO_URI and ensure the database exists.")

users = mongo.db.users

# SQLAlchemy Configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payroll.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Register blueprints (optional based on modularity)
# app.register_blueprint(auth_bp)
# app.register_blueprint(employee_bp)
# app.register_blueprint(payroll_bp)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/index', methods=['POST'])
def signup():
    name = request.form['name']
    username = request.form['username']
    email = request.form['email']
    phone = request.form['phone']
    password = request.form['password']

    try:
        existing_user = users.find_one({'email': email})
        if existing_user:
            return 'Email already registered.'

        users.insert_one({
            'name': name,
            'username': username,
            'email': email,
            'phone': phone,
            'password': password
        })
        return redirect(url_for('login'))

    except Exception as e:
        return f'Error signing up: {str(e)}'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form['email']
        password = request.form['password']
        try:
            user = users.find_one({'email': email, 'password': password})
            if user:
                session['username'] = user['username']
                return redirect(url_for('dashboard'))
            else:
                return 'Incorrect email or password'
        except Exception as e:
            return f'Error logging in: {str(e)}'

@app.route('/base')
def home():
    username = request.args.get('username', 'User')
    return render_template('base.html', user=username)

@app.route('/dashboard')
def dashboard():
    username = session.get('username', 'User')
    return render_template('dashboard.html', user=username)

@app.route('/add-employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        salary = float(request.form['salary'])
        department = request.form['department']

        if Employee.query.filter_by(email=email).first():
            flash('Email already exists.')
            return redirect(url_for('add_employee'))

        db.session.add(Employee(name=name, email=email, position=position, salary=salary, department=department))
        db.session.commit()
        flash('Employee added successfully!')
        return redirect(url_for('employee_list'))

    return render_template('add_employee.html')

@app.route('/employees')
def employee_list():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)

@app.route('/edit-employee/<int:id>', methods=['GET', 'POST'])
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
        return redirect(url_for('employee_list'))

    return render_template('edit_employee.html', employee=employee)

@app.route('/delete-employee/<int:id>')
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!')
    return redirect(url_for('employee_list'))

@app.route('/download-payslip/<int:id>')
def download_payslip(id):
    emp = Employee.query.get_or_404(id)
    tax = emp.salary * 0.1
    benefits = emp.salary * 0.05
    net_pay = emp.salary - tax + benefits
    period = 'May 2025'

    pdf_bytes = generate_payslip_pdf(emp, tax, benefits, net_pay, period)

    return send_file(
        io.BytesIO(pdf_bytes),
        mimetype='application/pdf',
        as_attachment=True,
        download_name=f"payslip_{emp.id}.pdf"
    )

@app.route('/generate-payslip', methods=['GET', 'POST'])
def generate_payslip():
    if request.method == 'POST':
        try:
            emp_name = request.form['employee_name']
            basic_salary = float(request.form['basic_salary'])
            allowances = float(request.form['allowances'])
            deductions = float(request.form['deductions'])

            if basic_salary < 0 or allowances < 0 or deductions < 0:
                flash('Values cannot be negative!', 'danger')
                return redirect(url_for('generate_payslip'))

            net_salary = basic_salary + allowances - deductions

            mongo.db.payslips.insert_one({
                'employee_name': emp_name,
                'basic_salary': basic_salary,
                'allowances': allowances,
                'deductions': deductions,
                'net_salary': net_salary,
                'date': datetime.now()
            })

            flash('Payslip generated successfully!', 'success')
            return redirect(url_for('view_payslip'))

        except ValueError:
            flash('Please enter valid numeric values.', 'danger')
        except Exception as e:
            flash(f'Error generating payslip: {str(e)}', 'danger')

        return redirect(url_for('generate_payslip'))

    return render_template('generate_payslip.html')

@app.route('/viewpayslip')
def view_payslip():
    payslips = mongo.db.payslips.find()
    return render_template('viewpayslip.html', payslips=payslips)

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
