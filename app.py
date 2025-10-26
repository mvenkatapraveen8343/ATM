from flask import Flask, render_template, request
from decimal import Decimal
import pymysql

app = Flask(__name__)

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'Praveen@8343',
    'database': 'ATM',
    'cursorclass': pymysql.cursors.DictCursor
}

def get_db_connection():
    return pymysql.connect(**db_config)

def db_init():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS Accounts (
            Acc_No VARCHAR(20) PRIMARY KEY,
            Name VARCHAR(100) NOT NULL,
            Balance DECIMAL(15,2) NOT NULL CHECK (Balance >= 0)
        )
    """)
    conn.commit()
    cursor.close()
    conn.close()

@app.route('/')
@app.route('/home')
def home():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Accounts")
    accounts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('home.html', accounts=accounts)

@app.route('/create', methods=['GET', 'POST'])
def createpage():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        name = request.form.get('name')
        balance = Decimal(request.form.get('balance'))

        if len(acc_no) < 10:
            return render_template('create.html', message='Invalid Account Number.', msg_type='error')
        if balance < Decimal('2000'):
            return render_template('create.html', message='Minimum Balance is ₹2000.', msg_type='error')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT Acc_No FROM Accounts WHERE Acc_No=%s", (acc_no,))
        existing = cursor.fetchone()

        if existing:
            cursor.close()
            conn.close()
            return render_template('create.html', message='Account already exists!!!', msg_type='error')

        cursor.execute(
            "INSERT INTO Accounts (Acc_No, Name, Balance) VALUES (%s, %s, %s)",
            (acc_no, name, balance))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('create.html', message='Account Created Successfully.', msg_type='success')

    return render_template('create.html')

@app.route('/balance', methods=['GET', 'POST'])
def balancepage():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Accounts WHERE Acc_No=%s", (acc_no,))
        account = cursor.fetchone()
        cursor.close()
        conn.close()
        if account:
            return render_template('balance.html', account=account, message="Details fetched successfully", msg_type='success')
        else:
            return render_template('balance.html', message="Account does not exist!!!", msg_type='error')

    return render_template('balance.html')

@app.route('/update', methods=['GET', 'POST'])
def updatepage():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        amount = Decimal(request.form.get('amount'))
        action = request.form.get('action')

        if amount <= 0:
            return render_template('update.html', message='Amount must be greater than zero.', msg_type='error')

        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Accounts WHERE Acc_No=%s", (acc_no,))
        account = cursor.fetchone()

        if not account:
            cursor.close()
            conn.close()
            return render_template('update.html', message='Account does not exist!!!', msg_type='error')

        balance = Decimal(account['Balance'])

        if action == 'deposit':
            new_balance = balance + amount
            cursor.execute("UPDATE Accounts SET Balance=%s WHERE Acc_No=%s", (new_balance, acc_no))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('update.html', message='Amount Deposited Successfully', msg_type='success')

        elif action == 'withdraw':
            if amount > balance:
                cursor.close()
                conn.close()
                return render_template('update.html', message="Insufficient Balance", msg_type='error')
            if balance - amount < Decimal('2000'):
                cursor.close()
                conn.close()
                return render_template('update.html', message='Please Maintain Minimum Balance ₹2000', msg_type='error')

            new_balance = balance - amount
            cursor.execute("UPDATE Accounts SET Balance=%s WHERE Acc_No=%s", (new_balance, acc_no))
            conn.commit()
            cursor.close()
            conn.close()
            return render_template('update.html', message='Amount Withdrawn Successfully', msg_type='success')

    return render_template('update.html')

@app.route('/delete', methods=['GET', 'POST'])
def deletepage():
    if request.method == 'POST':
        acc_no = request.form.get('acc_no')
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Accounts WHERE Acc_No=%s", (acc_no,))
        account = cursor.fetchone()

        if not account:
            cursor.close()
            conn.close()
            return render_template('delete.html', message='Account does not exist!!!', msg_type='error')

        cursor.execute("DELETE FROM Accounts WHERE Acc_No=%s", (acc_no,))
        conn.commit()
        cursor.close()
        conn.close()
        return render_template('delete.html', message='Account Deleted Successfully', msg_type='success')

    return render_template('delete.html')

if __name__ == '__main__':
    db_init()
    app.run(debug=True)