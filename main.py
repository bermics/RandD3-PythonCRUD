import mysql.connector
from mysql.connector import Error
import os
from dotenv import load_dotenv

# Load env
load_dotenv()

# Get conn from env
connection_params = {
    'host': os.getenv('DB_HOST'),
    'database': os.getenv('DB_NAME'),
    'user': os.getenv('DB_USER'),
    'password': os.getenv('DB_PASSWORD')
}


def ensure_database_and_tables():
    try:
        with mysql.connector.connect(**connection_params) as conn:
            cursor = conn.cursor()
            # Create database if it doesn't exist
            cursor.execute("CREATE DATABASE IF NOT EXISTS new_database2")
            cursor.execute("USE new_database2")  # Ensure the right database is used
            # Create CUSTOMERS table if it doesn't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS CUSTOMERS (
                    customer_id INT AUTO_INCREMENT PRIMARY KEY,
                    name VARCHAR(50) NOT NULL,
                    email VARCHAR(50) NOT NULL,
                    phone VARCHAR(15) NOT NULL,
                    address VARCHAR(100) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            conn.commit()
            print("Database and table are set up successfully.")
    except Error as e:
        print("Error ensuring database and tables:", e)


def validate_email(email):
    import re
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email) is not None


def get_non_empty_input(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Invalid input. This field cannot be empty. Please try again.")


def get_valid_email():
    while True:
        email = input("Enter email: ").strip()
        if validate_email(email):
            return email
        print("Invalid email format. Please enter a valid email.")


def get_valid_phone():
    while True:
        phone = input("Enter phone number (10 digits): ").strip()
        if phone.isdigit() and len(phone) == 10:
            return phone
        print("Invalid phone number. Please enter a 10-digit numeric phone number.")


def create_customer():
    name = get_non_empty_input("Enter customer name: ")
    email = get_valid_email()
    phone = get_valid_phone()
    address = get_non_empty_input("Enter address: ")

    try:
        with mysql.connector.connect(**connection_params) as conn:
            cursor = conn.cursor()
            query = "INSERT INTO CUSTOMERS (name, email, phone, address) VALUES (%s, %s, %s, %s)"
            cursor.execute(query, (name, email, phone, address))
            conn.commit()
            print("Customer record created successfully.")
    except Error as e:
        print("Error creating customer:", e)


def read_customers():
    print("\nChoose a field to filter by:")
    print("1. Customer ID")
    print("2. Name")
    print("3. Email")
    print("4. View all records")

    filter_choice = input("Enter choice (1-4): ").strip()

    if filter_choice == "1":
        customer_id = input("Enter the Customer ID to search: ").strip()
        if not customer_id.isdigit():
            print("Invalid ID, please enter a numeric ID.")
            return
        query = "SELECT * FROM CUSTOMERS WHERE customer_id = %s"
        params = (int(customer_id),)

    elif filter_choice == "2":
        name = get_non_empty_input("Enter the Name to search: ")
        query = "SELECT * FROM CUSTOMERS WHERE name LIKE %s"
        params = (f"%{name}%",)

    elif filter_choice == "3":
        email = get_valid_email()
        query = "SELECT * FROM CUSTOMERS WHERE email LIKE %s"
        params = (f"%{email}%",)

    elif filter_choice == "4":
        query = "SELECT * FROM CUSTOMERS"
        params = None

    else:
        print("Invalid input, returning to menu...")
        return

    try:
        with mysql.connector.connect(**connection_params) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params) if params else cursor.execute(query)
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]  # Get column names dynamically

            if not rows:
                print("No records found matching the search criteria.")
            else:
                # Print column headers dynamically
                print(" ".join(f"{col:<20}" for col in columns))

                # Print each row dynamically
                for row in rows:
                    print(" ".join(f"{str(item):<20}" for item in row))

    except Error as e:
        print("Error reading customers:", e)


def update_customer():
    customer_id = input("Enter the ID of the customer you want to update: ").strip()
    if not customer_id.isdigit():
        print("Invalid ID.")
        return
    customer_id = int(customer_id)

    new_name = get_non_empty_input("Enter new name: ")
    new_email = get_valid_email()
    new_phone = get_valid_phone()
    new_address = get_non_empty_input("Enter new address: ")

    try:
        with mysql.connector.connect(**connection_params) as conn:
            cursor = conn.cursor()
            update_query = """
                UPDATE CUSTOMERS SET name=%s, email=%s, phone=%s, address=%s WHERE customer_id=%s
            """
            cursor.execute(update_query, (new_name, new_email, new_phone, new_address, customer_id))
            conn.commit()
            print("Update was successful." if cursor.rowcount > 0 else "No record found with that ID.")
    except Error as e:
        print("Error updating customer:", e)


def delete_customer():
    customer_id = input("Enter the ID of the customer you want to delete: ").strip()
    if not customer_id.isdigit():
        print("Invalid ID.")
        return
    customer_id = int(customer_id)

    try:
        with mysql.connector.connect(**connection_params) as conn:
            cursor = conn.cursor()
            delete_query = "DELETE FROM CUSTOMERS WHERE customer_id = %s"
            cursor.execute(delete_query, (customer_id,))
            conn.commit()
            print("Delete successful." if cursor.rowcount > 0 else "No record found with that ID.")
    except Error as e:
        print("Error deleting customer:", e)


def main():
    ensure_database_and_tables()
    while True:
        print("\nMenu:")
        print("1. Create a new customer")
        print("2. Read customer records")
        print("3. Update a customer record")
        print("4. Delete a customer record")
        print("5. Exit")

        choice = input("Enter choice (1-5): ")
        if choice == "1":
            create_customer()
        elif choice == "2":
            read_customers()
        elif choice == "3":
            update_customer()
        elif choice == "4":
            delete_customer()
        elif choice == "5":
            print("Exiting...")
            break
        else:
            print("Invalid choice. Try again.")


if __name__ == "__main__":
    main()
