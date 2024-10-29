from flask import Flask, render_template, request, redirect, url_for
import mysql.connector
from datetime import date

app = Flask(__name__)

# Database configuration
db_config = {
    'user': 'root',
    'password': 'root',
    'host': 'localhost',
    'database': 'finance_tracker'
}

# Function to create a database connection
def get_db_connection():
    return mysql.connector.connect(**db_config)

# Route for Dashboard
@app.route('/')
def dashboard():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch overall budget
    cursor.execute("SELECT overall_budget FROM settings LIMIT 1")
    result = cursor.fetchone()
    overall_budget = result['overall_budget'] if result else 0

    # Fetch today's income and expenses
    cursor.execute("SELECT SUM(amount) as total_income FROM income WHERE date = CURDATE()")
    total_income = cursor.fetchone()['total_income'] or 0

    cursor.execute("SELECT SUM(amount) as total_expense FROM expenses WHERE date = CURDATE()")
    total_expense = cursor.fetchone()['total_expense'] or 0

    # Fetch budget by categories (income and expenses grouped by category)
    cursor.execute("SELECT category, SUM(amount) as total FROM income GROUP BY category")
    income_by_category = cursor.fetchall()

    cursor.execute("SELECT category, SUM(amount) as total FROM expenses GROUP BY category")
    expense_by_category = cursor.fetchall()

    cursor.close()
    connection.close()

    return render_template('dashboard.html', overall_budget=overall_budget, total_income=total_income,
                           total_expense=total_expense, income_by_category=income_by_category, 
                           expense_by_category=expense_by_category)

# Route for Income Management
@app.route('/income', methods=['GET', 'POST'])
def income_management():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Ensure the field names match exactly with those in the form
        date = request.form.get('income-date')  # Use .get() to avoid KeyError
        category = request.form.get('income-source')
        amount = request.form.get('income-amount')

        if date and category and amount:  # Check if all fields are filled
            cursor.execute("INSERT INTO income (date, category, amount) VALUES (%s, %s, %s)",
                           (date, category, amount))
            connection.commit()

        return redirect(url_for('income_management'))

    # Fetch all income records
    cursor.execute("SELECT * FROM income")
    income_records = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('income.html', income_records=income_records)

# Route for Expense Management
@app.route('/expense', methods=['GET', 'POST'])
def expense_management():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Ensure the field names match exactly with those in the form
        date = request.form.get('expense-date')  # Use .get() to avoid KeyError
        category = request.form.get('expense-category')
        amount = request.form.get('expense-amount')

        if date and category and amount:  # Check if all fields are filled
            cursor.execute("INSERT INTO expenses (date, category, amount) VALUES (%s, %s, %s)",
                           (date, category, amount))
            connection.commit()

        return redirect(url_for('expense_management'))

    # Fetch all expense records
    cursor.execute("SELECT * FROM expenses")
    expense_records = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('expense.html', expense_records=expense_records)

# Route for Reports
@app.route('/reports')
def reports():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    # Fetch income and expenses grouped by category
    cursor.execute("SELECT category, SUM(amount) as total FROM income GROUP BY category")
    income_by_category = cursor.fetchall()

    cursor.execute("SELECT category, SUM(amount) as total FROM expenses GROUP BY category")
    expense_by_category = cursor.fetchall()

    cursor.close()
    connection.close()
    return render_template('reports.html', income_by_category=income_by_category, expense_by_category=expense_by_category)

# Route for Settings
@app.route('/settings', methods=['GET', 'POST'])
def settings():
    connection = get_db_connection()
    cursor = connection.cursor(dictionary=True)

    if request.method == 'POST':
        # Update overall budget
        new_budget = request.form['overall_budget']
        cursor.execute("UPDATE settings SET overall_budget = %s WHERE id = 1", (new_budget,))
        connection.commit()

        return redirect(url_for('settings'))

    # Fetch current budget setting
    cursor.execute("SELECT overall_budget FROM settings LIMIT 1")
    overall_budget = cursor.fetchone()['overall_budget']

    cursor.close()
    connection.close()
    return render_template('settings.html', overall_budget=overall_budget)

if __name__ == '__main__':
    app.run(debug=True)
