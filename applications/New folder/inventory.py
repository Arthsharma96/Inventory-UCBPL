import sqlite3
from datetime import datetime

def connect_to_database():
    # Connect to SQLite database (creates a new file 'inventory.db' if not exists)
    conn = sqlite3.connect('inventory.db')
    cursor = conn.cursor()

    # Create table if not exists
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            price REAL NOT NULL,
            date_added DATE NOT NULL
        )
    ''')
    conn.commit()

    return conn, cursor

def display_inventory(cursor):
    # Display all items in the inventory
    cursor.execute("SELECT * FROM items")
    items = cursor.fetchall()

    if not items:
        print("No items in the inventory.")
    else:
        print("Inventory:")
        for item in items:
            print(f"ID: {item[0]}, Name: {item[1]}, Quantity: {item[2]}, Price: {item[3]}, Date Added: {item[4]}")

def add_item(cursor):
    # Add a new item to the inventory with user input
    name = input("Enter the item name: ")
    quantity = int(input("Enter the quantity: "))
    price = float(input("Enter the price: "))

    current_date = datetime.now().date()
    cursor.execute("INSERT INTO items (name, quantity, price, date_added) VALUES (?, ?, ?, ?)",
                   (name, quantity, price, current_date))
    cursor.connection.commit()
    print("Item added successfully.")

def update_item(cursor):
    # Update quantity and price of an existing item with user input
    item_id = int(input("Enter the item ID to update: "))
    new_quantity = int(input("Enter the new quantity: "))
    new_price = float(input("Enter the new price: "))

    cursor.execute("UPDATE items SET quantity=?, price=? WHERE id=?", (new_quantity, new_price, item_id))
    cursor.connection.commit()
    print("Item updated successfully.")

def delete_item(cursor):
    # Delete an item from the inventory with user input
    item_id = int(input("Enter the item ID to delete: "))

    cursor.execute("DELETE FROM items WHERE id=?", (item_id,))
    cursor.connection.commit()
    print("Item deleted successfully.")

def main():
    conn, cursor = connect_to_database()

    while True:
        print("\nOptions:")
        print("1. Display Inventory")
        print("2. Add Item")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Exit")

        choice = input("Enter your choice (1-5): ")

        if choice == '1':
            display_inventory(cursor)
        elif choice == '2':
            add_item(cursor)
        elif choice == '3':
            update_item(cursor)
        elif choice == '4':
            delete_item(cursor)
        elif choice == '5':
            print("Exiting program.")
            # Commit changes to the database before closing the connection
            cursor.connection.commit()
            break
        else:
            print("Invalid choice. Please enter a number between 1 and 5.")

    cursor.close()
    conn.close()

if __name__ == "__main__":
    main()
