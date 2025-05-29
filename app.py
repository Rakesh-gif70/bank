from flask import Flask, render_template, request, redirect, url_for, session, flash
import json
import os

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Change this!

DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
ACCOUNTS_FILE = os.path.join(DATA_DIR, 'accounts.json')

# Load/save functions
def load_data(file_path):
    if not os.path.exists(file_path):
        return {}
    with open(file_path) as f:
        return json.load(f)

def save_data(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)

@app.route('/')
def home():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return redirect(url_for('login'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data(USERS_FILE)
        if username in users:
            flash('Username already exists!')
            return redirect(url_for('register'))
        users[username] = {'password': password}
        save_data(USERS_FILE, users)
        # Create an account for user with initial balance
        accounts = load_data(ACCOUNTS_FILE)
        accounts[username] = {'balance': 1000}  # Starting with 1000 units
        save_data(ACCOUNTS_FILE, accounts)
        flash('Registration successful! Please login.')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        users = load_data(USERS_FILE)
        if username in users and users[username]['password'] == password:
            session['username'] = username
            return redirect(url_for('dashboard'))
        flash('Invalid credentials!')
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    accounts = load_data(ACCOUNTS_FILE)
    user_acc = accounts.get(session['username'])
    return render_template('dashboard.html', balance=user_acc['balance'])

@app.route('/transfer', methods=['GET', 'POST'])
def transfer():
    if 'username' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        recipient = request.form['recipient']
        amount = float(request.form['amount'])
        accounts = load_data(ACCOUNTS_FILE)
        sender = session['username']

        if recipient not in accounts:
            flash('Recipient does not exist!')
            return redirect(url_for('transfer'))

        if accounts[sender]['balance'] < amount:
            flash('Insufficient balance!')
            return redirect(url_for('transfer'))

        # Transfer money
        accounts[sender]['balance'] -= amount
        accounts[recipient]['balance'] += amount
        save_data(ACCOUNTS_FILE, accounts)
        flash(f'Successfully transferred {amount} to {recipient}')
        return redirect(url_for('dashboard'))
    return render_template('transfer.html')

@app.route('/logout')
def logout():
    session.pop('username', None)
    flash('Logged out successfully.')
    return redirect(url_for('login'))

if __name__ == '__main__':
    os.makedirs(DATA_DIR, exist_ok=True)
    app.run(debug=True)