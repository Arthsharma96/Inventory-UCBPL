from flask import Flask, render_template, request, redirect, url_for, flash
from datetime import datetime
import sqlite3

app = Flask(__name__)

def connect_to_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints

    cursor.execute('''
CREATE TABLE IF NOT EXISTS items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    quantity INTEGER NOT NULL,
    unit TEXT NOT NULL,
    cost_per_unit REAL NOT NULL,
    total_cost REAL NOT NULL,
    selling_price REAL NOT NULL,
    supplier TEXT,
    date_added DATE NOT NULL,
    last_updated DATE,
    location TEXT,
    min_stock_level INTEGER,
    max_stock_level INTEGER,
    reorder_quantity INTEGER,
    notes TEXT,
    current_date DATE NOT NULL
)
''')

    cursor.execute('''
CREATE TABLE IF NOT EXISTS issued_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,  -- Foreign key to items table
    name TEXT,
    quantity_issued INTEGER,
    date_issued DATE,
    department_name TEXT
)
''')
    
    cursor.execute('''
CREATE TABLE IF NOT EXISTS ledger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    item_id INTEGER,
    transaction_type TEXT,
    quantity INTEGER,
    transaction_date DATE,
    FOREIGN KEY (item_id) REFERENCES items (id)
)
''')

    conn.commit()

    return conn, cursor

@app.route('/')
def welcome():
    return render_template('welcome.html')

@app.route('/display_inventory')
def display_inventory():
    conn, cursor = connect_to_database()
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()
    conn.close()

    return render_template('inventory.html', items=items)

@app.route('/search_inventory', methods=['GET'])
def search_inventory():
    conn, cursor = connect_to_database()
    search_term = request.args.get('search', '').strip()
    cursor.execute("SELECT * FROM items WHERE name LIKE ?", ('%' + search_term + '%',))
    items = cursor.fetchall()
    conn.close()
    return render_template('inventory.html', items=items)

@app.route('/delete_item/<int:item_id>')
def delete_item(item_id):
    conn, cursor = connect_to_database()
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    conn.commit()
    conn.close()
    return redirect(url_for('display_inventory'))

@app.route('/update_item/<int:item_id>', methods=['GET', 'POST'])
def update_item(item_id):
    conn, cursor = connect_to_database()
    if request.method == 'POST':
        quantity = int(request.form['quantity'])
        price = float(request.form['price'])
        cursor.execute("UPDATE items SET quantity=?, selling_price=?, last_updated=? WHERE id=?", (quantity, price, datetime.now(), item_id))
        conn.commit()
        conn.close()
        return redirect(url_for('display_inventory'))
    cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = cursor.fetchone()
    conn.close()
    return render_template('update_item.html', item=item)

@app.route('/issue_item', methods=['GET', 'POST'])
def issue_item():
    conn, cursor = connect_to_database()
    item = None
    if request.method == 'POST':
        item_id = request.form.get('item_id')
        quantity_issued = int(request.form['quantity_issued'])
        department_name = request.form['department_name']
        if not item_id or not item_id.isdigit():
            flash("Invalid item ID. Please enter a valid number.", 'danger')
            conn.close()
            return redirect(url_for('issue_item'))
        item_id = int(item_id)
        cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
        item = cursor.fetchone()
        if item and item[2] >= quantity_issued > 0:
            try:
                cursor.execute("UPDATE items SET quantity=? WHERE id=?", (item[2] - quantity_issued, item_id))
                cursor.execute("INSERT INTO issued_items (item_id, name, quantity_issued, date_issued, department_name) VALUES (?, ?, ?, ?, ?)",
                                (item_id, item[1], quantity_issued, datetime.now().date(), department_name))
                cursor.execute("INSERT INTO ledger (item_id, transaction_type, quantity, transaction_date) VALUES (?, ?, ?, ?)",
                                (item_id, 'issue', quantity_issued, datetime.now().date()))
                conn.commit()
                conn.close()
                flash(f"{quantity_issued} {item[1]} issued to {department_name}.", 'success')
                return redirect(url_for('view_issued_items'))
            except Exception as e:
                flash(f"Error issuing item: {str(e)}", 'danger')
                conn.close()
        else:
            flash("Failed to issue item. Please check the entered details.", 'danger')
    conn.close()
    return render_template('issue_item.html', item=item)

@app.route('/view_issued_items', methods=['GET', 'POST'])
def view_issued_items():
    conn, cursor = connect_to_database()
    cursor.execute("SELECT * FROM issued_items")
    issued_items = cursor.fetchall()
    conn.close()
    return render_template('view_issued_items.html', issued_items=issued_items)

@app.route('/view_ledger/<int:item_id>')
def view_ledger(item_id):
    conn, cursor = connect_to_database()
    cursor.execute("SELECT * FROM items WHERE id=?", (item_id,))
    item = cursor.fetchone()
    if item:
        cursor.execute("SELECT * FROM ledger WHERE item_id=?", (item_id,))
        ledger_data = cursor.fetchall()
        conn.close()
        return render_template('view_ledger.html', item=item, ledger_data=ledger_data)
    else:
        flash("Item not found.", 'danger')
        conn.close()
        return redirect(url_for('display_inventory'))

@app.route('/add_item', methods=['GET', 'POST'])
def add_item():
    if request.method == 'POST':
        conn, cursor = connect_to_database()
        id = request.form['id']
        name = request.form['name']
        quantity = int(request.form['quantity'])
        unit = request.form['unit']
        cost_per_unit = float(request.form['cost_per_unit'])
        selling_price = float(request.form['selling_price'])
        supplier = request.form['supplier']
        date_added_str = request.form['date_added']
        date_added = datetime.now().date() if not date_added_str else datetime.strptime(date_added_str, '%Y-%m-%d').date()
        location = request.form['location']
        min_stock_level = int(request.form['min_stock_level'])
        max_stock_level = int(request.form['max_stock_level'])
        reorder_quantity = int(request.form['reorder_quantity'])
        notes = request.form['notes']
        current_date = datetime.now().date()
        cursor.execute("INSERT INTO items (id, name, quantity, unit, cost_per_unit, total_cost, selling_price, supplier, date_added, location, min_stock_level, max_stock_level, reorder_quantity, notes, current_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                        (id, name, quantity, unit, cost_per_unit, quantity * cost_per_unit, selling_price, supplier, date_added, location, min_stock_level, max_stock_level, reorder_quantity, notes, current_date))
        conn.commit()
        conn.close()
        return redirect(url_for('display_inventory'))
    current_date = datetime.now().date()
    return render_template('add_item.html', current_date=current_date)

if __name__ == '__main__':
    app.secret_key = 'ucbpl'  
    app.run(debug=True)
