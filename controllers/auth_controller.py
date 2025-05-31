from flask import Blueprint, request, redirect, url_for, flash, session

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if username == 'admin' and password == 'admin':
        session['user'] = username
        return redirect(url_for('main.dashboard', user=username))
    else:
        flash('Invalid credentials')
        return redirect(url_for('index'))

@auth_bp.route('/logout')
def logout():
    session.pop('user', None)
    flash('Logged out successfully.')
    return redirect(url_for('main.index'))
