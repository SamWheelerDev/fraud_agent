from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, session
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import os
import json
from datetime import datetime, timedelta
import random

app = Flask(__name__)
app.secret_key = 'dev_secret_key_transaction_lookup'

# Database setup
def init_db():
    conn = sqlite3.connect('transaction_lookup.db')
    cursor = conn.cursor()
    
    # Create users table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL
    )
    ''')
    
    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        transaction_id TEXT UNIQUE NOT NULL,
        card_number TEXT NOT NULL,
        amount REAL NOT NULL,
        merchant_name TEXT NOT NULL,
        transaction_date TEXT NOT NULL,
        status TEXT NOT NULL
    )
    ''')
    
    # Add demo user if not exists
    cursor.execute("SELECT * FROM users WHERE username = 'demo'")
    if not cursor.fetchone():
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                   ('demo', generate_password_hash('password')))
    
    # Add sample transactions if table is empty
    cursor.execute("SELECT COUNT(*) FROM transactions")
    if cursor.fetchone()[0] == 0:
        # Generate sample transaction data
        card_numbers = [
            "4111XXXXXXXXXXXX", 
            "5555XXXXXXXXXXXX", 
            "3782XXXXXXXXXXX",
            "6011XXXXXXXXXXXX"
        ]
        merchants = [
            "Amazon", 
            "Walmart", 
            "Target", 
            "Best Buy", 
            "Apple Store",
            "Netflix", 
            "Uber", 
            "DoorDash",
            "Shell Gas",
            "Unknown Merchant"
        ]
        statuses = ["Pending", "Completed", "Declined"]
        
        # Generate 50 sample transactions
        for i in range(50):
            tx_date = (datetime.now() - timedelta(days=random.randint(1, 60))).strftime("%Y-%m-%d")
            tx_id = f"TX{random.randint(10000000, 99999999)}"
            card = random.choice(card_numbers)
            amount = round(random.uniform(5.00, 500.00), 2)
            merchant = random.choice(merchants)
            status = random.choice(statuses)
            
            cursor.execute(
                "INSERT INTO transactions (transaction_id, card_number, amount, merchant_name, transaction_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                (tx_id, card, amount, merchant, tx_date, status)
            )
    
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
        return redirect(url_for('search'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        conn = sqlite3.connect('transaction_lookup.db')
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = cursor.fetchone()
        conn.close()
        
        if user and check_password_hash(user[2], password):
            session['user_id'] = user[0]
            session['username'] = user[1]
            flash('Login successful!', 'success')
            return redirect(url_for('search'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

@app.route('/search', methods=['GET'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('search.html')

@app.route('/api/search', methods=['POST'])
def api_search():
    if 'user_id' not in session:
        return jsonify({'error': 'Not authenticated'}), 401
    
    data = request.json
    search_term = data.get('search_term', '')
    
    conn = sqlite3.connect('transaction_lookup.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Search in multiple columns
    cursor.execute("""
        SELECT * FROM transactions 
        WHERE transaction_id LIKE ? 
        OR card_number LIKE ? 
        OR merchant_name LIKE ?
        LIMIT 20
    """, (f'%{search_term}%', f'%{search_term}%', f'%{search_term}%'))
    
    rows = cursor.fetchall()
    transactions = [dict(row) for row in rows]
    conn.close()
    
    return jsonify({'transactions': transactions})

@app.route('/transaction/<transaction_id>')
def transaction_detail(transaction_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = sqlite3.connect('transaction_lookup.db')
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute("SELECT * FROM transactions WHERE transaction_id = ?", (transaction_id,))
    transaction = cursor.fetchone()
    conn.close()
    
    if not transaction:
        flash('Transaction not found.', 'error')
        return redirect(url_for('search'))
    
    transaction = dict(transaction)
    return render_template('transaction_detail.html', transaction=transaction)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')