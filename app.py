from flask import Flask, render_template, request, redirect, url_for, flash, send_file
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
app.config["MONGO_URI"] = "mongodb+srv://chintakayalamutyalu:Demudu%4021@cluster0.mban80h.mongodb.net/"
mongo = PyMongo(app)
users = mongo.db.users

app.secret_key = 'mutyalu1234'

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///payroll.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

with app.app_context():
    db.create_all()

# Register blueprints
# app.register_blueprint(auth_bp)
# app.register_blueprint(employee_bp)
# app.register_blueprint(payroll_bp)

@app.route('/')
def index():
    return render_template('index.html')

# Signup route
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

        new_user = {
            'name': name,
            'username': username,
            'email': email,
            'phone': phone,
            'password': password
        }
        users.insert_one(new_user)
        return redirect(url_for('login'))  

    except Exception as e:
        return 'Error signing up'


# Login route
@app.route('/login', methods=['GET','POST'])
def login():
    print("login is called", request.method)
    if request.method == "GET":
        return render_template("login.html")
    else:
        email = request.form['email']
        password = request.form['password']
        print("email, password", email, password)
        try:
            user = users.find_one({'email': email, 'password': password})
            print("user", user)
            if user:
                session['username'] = user['username']  
                return redirect(url_for('dashboard'))
            else:
                return 'Incorrect email or password'
        except Exception as e:
            return 'Error logging in'


#  This route renders base.html after login
@app.route('/base')
def home():
    username = request.args.get('username', 'User')
    return render_template('base.html', user=username)

@app.route('/dashboard')
def dashboard():
    username = session.get('username', 'User')  # ✅ get from session
    return render_template('dashboard.html', user=username)




# Add employee
@app.route('/add-employee', methods=['GET', 'POST'])
def add_employee():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        position = request.form['position']
        salary = float(request.form['salary'])
        department = request.form['department']

        existing = Employee.query.filter_by(email=email).first()
        if existing:
            flash('Email already exists.')
            return redirect(url_for('add_employee'))

        employee = Employee(name=name, email=email, position=position, salary=salary, department=department)
        db.session.add(employee)
        db.session.commit()
        flash('Employee added successfully!')
        return redirect(url_for('employee_list'))

    return render_template('add_employee.html')

# List employees
@app.route('/employees')
def employee_list():
    employees = Employee.query.all()
    return render_template('employee_list.html', employees=employees)

# Edit employee
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

# Delete employee
@app.route('/delete-employee/<int:id>')
def delete_employee(id):
    employee = Employee.query.get_or_404(id)
    db.session.delete(employee)
    db.session.commit()
    flash('Employee deleted successfully!')
    return redirect(url_for('employee_list'))

# PDF generator
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

# Generate payslip
@app.route('/generate-payslip', methods=['GET', 'POST'])
def generate_payslip():
    if request.method == 'POST':
        try:
            emp_name = request.form['employee_name']
            basic_salary = float(request.form['basic_salary'])
            allowances = float(request.form['allowances'])
            deductions = float(request.form['deductions'])

            # Ensure no negative salaries
            if basic_salary < 0 or allowances < 0 or deductions < 0:
                flash('Values cannot be negative!', 'danger')
                return redirect(url_for('generate_payslip'))

            net_salary = basic_salary + allowances - deductions

            # Save to MongoDB
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
            return redirect(url_for('generate_payslip'))

        except Exception as e:
            flash(f'Error generating payslip: {str(e)}', 'danger')
            return redirect(url_for('generate_payslip'))

    return render_template('generate_payslip.html')

# View payslips
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
