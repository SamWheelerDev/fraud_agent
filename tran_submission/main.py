from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'dev_secret_key_dispute_submission'

# Database setup
def init_db():
    conn = sqlite3.connect('dispute_submission.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create disputes table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS disputes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT NOT NULL,
        card_number TEXT NOT NULL,
        amount REAL NOT NULL,
        merchant_name TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        dispute_reason TEXT NOT NULL,
        cardholder_name TEXT NOT NULL,
        additional_details TEXT,
        submission_date TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    # Add demo user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'demo'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   ('demo', generate_password_hash('password')))
    
    conn.commit()
    conn.close()

# Initialize database at startup
@app.before_first_request
def before_first_request():
    init_db()

# Routes
@app.route('/')
def index():
    if 'user_id' in session:
        return redirect(url_for('dispute_form'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('dispute_submission.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('dispute_form'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/dispute-form', methods=['GET'])
def dispute_form():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dispute_form.html')

@app.route('/submit-dispute', methods=['POST'])
def submit_dispute():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    try:
        # Get form data
        transaction_id = request.form['transaction_id']
        card_number = request.form['card_number']
        amount = float(request.form['amount'])
        merchant_name = request.form['merchant_name']
        transaction_date = request.form['transaction_date']
        dispute_reason = request.form['dispute_reason']
        cardholder_name = request.form['cardholder_name']
        additional_details = request.form.get('additional_details', '')
        
        # Validate required fields
        if not all([transaction_id, card_number, amount, merchant_name, 
                   transaction_date, dispute_reason, cardholder_name]):
            flash('All required fields must be filled out.', 'error')
            return redirect(url_for('dispute_form'))
        
        # Insert into database
        conn = sqlite3.connect('dispute_submission.db')
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO disputes 
            (transaction_id, card_number, amount, merchant_name, transaction_date, 
             dispute_reason, cardholder_name, additional_details, submission_date, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            transaction_id, 
            card_number, 
            amount, 
            merchant_name, 
            transaction_date, 
            dispute_reason, 
            cardholder_name, 
            additional_details, 
            datetime.now().strftime('%Y-%m-%d'), 
            'Pending'
        ))
        
        conn.commit()
        dispute_id = cursor.lastrowid
        conn.close()
        
        flash('Dispute submitted successfully! Reference ID: ' + str(dispute_id), 'success')
        return redirect(url_for('dispute_confirmation', dispute_id=dispute_id))
    
    except Exception as e:
        flash(f'Error submitting dispute: {str(e)}', 'error')
        return redirect(url_for('dispute_form'))

@app.route('/dispute-confirmation/<int:dispute_id>')
def dispute_confirmation(dispute_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('dispute_submission.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM disputes WHERE id = ?", (dispute_id,))
    dispute = cursor.fetchone()
    conn.close()
    
    if not dispute:
        flash('Dispute not found.', 'error')
        return redirect(url_for('dispute_form'))
    
    return render_template('dispute_confirmation.html', dispute=dict(dispute))

@app.route('/view-disputes')
def view_disputes():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('dispute_submission.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM disputes ORDER BY submission_date DESC")
    disputes = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return render_template('view_disputes.html', disputes=disputes)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
