import sqlite3
from datetime import datetime
from prettytable import PrettyTable
from tkinter import *
from tkinter import ttk

def connect_to_database():
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

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
        current_date DATE NOT NULL  -- Add the new column for current_date
    )
    ''')

    conn.commit()

    return conn, cursor

def display_inventory(cursor, tree):
    tree.delete(*tree.get_children())
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    if not items:
        print("No items in the inventory.")
    else:
        for item in items:
            try:
                # Convert date strings to more readable formats if needed
                date_added = datetime.strptime(item[8], '%Y-%m-%d').strftime('%d-%m-%Y')
                current_date = datetime.strptime(item[14], '%Y-%m-%d').strftime('%d-%m-%Y')  # Adjust index if needed
            except ValueError:
                # Handle the case where the date is not in the expected format
                current_date = "N/A"  # Set a default value or handle it as needed

            # Append the dates to the item details
            item_with_dates = item[:8] + (date_added,) + item[9:14] + (current_date,) + item[15:]
            tree.insert("", "end", values=item_with_dates)


def add_item(cursor, name, quantity, unit, cost_per_unit, selling_price, supplier, date_added, location, min_stock_level, max_stock_level, reorder_quantity, notes):
    current_date = datetime.now().date()
    cursor.execute("INSERT INTO items (name, quantity, unit, cost_per_unit, total_cost, selling_price, supplier, date_added, location, min_stock_level, max_stock_level, reorder_quantity, notes, current_date) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                   (name, quantity, unit, cost_per_unit, quantity * cost_per_unit, selling_price, supplier, date_added, location, min_stock_level, max_stock_level, reorder_quantity, notes, current_date))
    cursor.connection.commit()


def update_item(cursor, item_id, new_quantity, new_unit, new_cost_per_unit, new_selling_price, new_supplier, new_location, new_min_stock_level, new_max_stock_level, new_reorder_quantity, new_notes):
    current_date = datetime.now().date()
    cursor.execute("UPDATE items SET quantity=?, unit=?, cost_per_unit=?, total_cost=?, selling_price=?, supplier=?, last_updated=?, location=?, min_stock_level=?, max_stock_level=?, reorder_quantity=?, notes=? WHERE id=?",
                   (new_quantity, new_unit, new_cost_per_unit, new_quantity * new_cost_per_unit, new_selling_price, new_supplier, current_date, new_location, new_min_stock_level, new_max_stock_level, new_reorder_quantity, new_notes, item_id))
    cursor.connection.commit()

def delete_item(cursor, item_id):
    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    cursor.connection.commit()

def main():
    conn, cursor = connect_to_database()

    root = Tk()
    root.title("Inventory Management")

    tree = ttk.Treeview(root, columns=("ID", "Name", "Quantity", "Unit", "Cost per Unit", "Total Cost",
                                   "Selling Price", "Supplier", "Date Added", "Last Updated",
                                   "Location", "Min Stock Level", "Max Stock Level", "Reorder Quantity", "Notes"))
    tree.heading("#0", text="ID")
    tree.heading("#1", text="Name")
    tree.heading("#2", text="Quantity")
    tree.heading("#3", text="Unit")
    tree.heading("#4", text="Cost per Unit")
    tree.heading("#5", text="Total Cost")
    tree.heading("#6", text="Selling Price")
    tree.heading("#7", text="Supplier")
    tree.heading("#8", text="Date Added")
    tree.heading("#9", text="Last Updated")
    tree.heading("#10", text="Location")
    tree.heading("#11", text="Min Stock Level")
    tree.heading("#12", text="Max Stock Level")
    tree.heading("#13", text="Reorder Quantity")
    tree.heading("#14", text="Notes")

    tree.pack()

    display_inventory(cursor, tree)

    def add_item_gui():
        add_window = Toplevel(root)
        add_window.title("Add Item")

        name_label = Label(add_window, text="Name:")
        name_entry = Entry(add_window)
        name_label.grid(row=0, column=0)
        name_entry.grid(row=0, column=1)

        quantity_label = Label(add_window, text="Quantity:")
        quantity_entry = Entry(add_window)
        quantity_label.grid(row=1, column=0)
        quantity_entry.grid(row=1, column=1)

        unit_label = Label(add_window, text="Unit:")
        unit_entry = Entry(add_window)
        unit_label.grid(row=2, column=0)
        unit_entry.grid(row=2, column=1)

        cost_per_unit_label = Label(add_window, text="Cost per Unit:")
        cost_per_unit_entry = Entry(add_window)
        cost_per_unit_label.grid(row=3, column=0)
        cost_per_unit_entry.grid(row=3, column=1)

        selling_price_label = Label(add_window, text="Selling Price:")
        selling_price_entry = Entry(add_window)
        selling_price_label.grid(row=4, column=0)
        selling_price_entry.grid(row=4, column=1)

        supplier_label = Label(add_window, text="Supplier:")
        supplier_entry = Entry(add_window)
        supplier_label.grid(row=5, column=0)
        supplier_entry.grid(row=5, column=1)

        date_added_label = Label(add_window, text="Date Added:")
        date_added_entry = Entry(add_window)
        date_added_label.grid(row=6, column=0)
        date_added_entry.grid(row=6, column=1)

        # Set the default value for the Date Added field
        current_date = datetime.now().date()
        date_added_entry.insert(0, current_date)

        location_label = Label(add_window, text="Location:")
        location_entry = Entry(add_window)
        location_label.grid(row=7, column=0)
        location_entry.grid(row=7, column=1)

        min_stock_level_label = Label(add_window, text="Min Stock Level:")
        min_stock_level_entry = Entry(add_window)
        min_stock_level_label.grid(row=8, column=0)
        min_stock_level_entry.grid(row=8, column=1)

        max_stock_level_label = Label(add_window, text="Max Stock Level:")
        max_stock_level_entry = Entry(add_window)
        max_stock_level_label.grid(row=9, column=0)
        max_stock_level_entry.grid(row=9, column=1)

        reorder_quantity_label = Label(add_window, text="Reorder Quantity:")
        reorder_quantity_entry = Entry(add_window)
        reorder_quantity_label.grid(row=10, column=0)
        reorder_quantity_entry.grid(row=10, column=1)

        notes_label = Label(add_window, text="Notes:")
        notes_entry = Entry(add_window)
        notes_label.grid(row=11, column=0)
        notes_entry.grid(row=11, column=1)

        add_window.grid_rowconfigure(12, weight=1)  # Allow the last row to expand
        add_window.grid_columnconfigure(1, weight=1)  # Allow the second column to expand

        def add_item_to_database():
            add_item(cursor, name_entry.get(), int(quantity_entry.get()), unit_entry.get(),
            float(cost_per_unit_entry.get()), float(selling_price_entry.get()), supplier_entry.get(),
            date_added_entry.get(),  # Pass the Date Added from the entry
            location_entry.get(), int(min_stock_level_entry.get()), int(max_stock_level_entry.get()),
            int(reorder_quantity_entry.get()), notes_entry.get())

            display_inventory(cursor, tree)
            add_window.destroy()

        add_button = Button(add_window, text="Add Item", command=add_item_to_database)
        add_button.grid(row=12, columnspan=2)

    add_button = Button(root, text="Add Item", command=add_item_gui)
    add_button.pack()

    # Similar functions for update and delete with corresponding GUI elements...

    root.mainloop()

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
