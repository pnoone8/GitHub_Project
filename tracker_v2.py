'''
Importing SQL module to access and edit database.
Also importing date info for tagging later in the program
'''

import sqlite3
from datetime import date

# Connecting to database and establishing cursor
try:
    db = sqlite3.connect("./finances.db")
    cursor = db.cursor()
except sqlite3.Error as e:
    print("Error: Could not connect to the database. "
          f"Error details: {e}.")
    raise e

# Defining today's date
today = date.today()


class Expense:
    '''Defining Expense as its own class'''

    def __init__(self, transaction_id, recipient, amount,
                 transaction_date):
        self.transaction_id = transaction_id
        self.recipient = recipient
        self.amount = amount
        self.transaction_date = transaction_date

    def add(self, user_choice):
        '''Adds an expense to the database to the correct category'''

        category_map = {
            1: "Bills",
            2: "Personal",
            3: "Travel",
            4: "Food and Drink"}

        if user_choice in category_map:
            category = category_map[user_choice]
            table_name = f"Expenses_{category.replace(" ", "_")}"

            try:
                cursor.execute(f'''INSERT INTO {table_name} (recipient,
                               amount, date) VALUES(?, ?, ?)''',
                               (self.recipient, self.amount,
                                self.transaction_date))
                db.commit()
            except sqlite3.Error as e:
                print("Error: The expense could not be added. "
                      f"Error details: {e}")
                db.rollback()
                raise e

        if user_choice == 5:
            category = input("\nWhat would you like to call the new"
                             " category?\n")
            table_name = f"Expenses_{category.replace(" ", "_")}"

            try:
                cursor.execute(f'''CREATE TABLE IF NOT EXISTS
                               {table_name} (id INTEGER PRIMARY KEY,
                               recipient VARCHAR(255), amount DECIMAL
                               (10, 2), date DATE)''')
                cursor.execute(f'''INSERT INTO {table_name} (recipient,
                               amount, date) VALUES(?, ?, ?)''',
                               (self.recipient, self.amount,
                               self.transaction_date))
                db.commit()
            except sqlite3.Error as e:
                print("Error: Table could not be created.")
                db.rollback()
                raise e

        return category


class Income:
    '''Defining Income as its own class'''

    def __init__(self, transaction_id, payer, amount,
                 transaction_date):
        self.transaction_id = transaction_id
        self.payer = payer
        self.amount = amount
        self.transaction_date = transaction_date


def create_tables():
    '''Creates tables for both expenses and income'''

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses_Bills
                        (id INTEGER PRIMARY KEY, recipient VARCHAR(255),
                        amount DECIMAL(10, 2), date DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses_Personal
                        (id INTEGER PRIMARY KEY, recipient VARCHAR(255),
                        amount DECIMAL(10, 2), date DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Expenses_Travel
                        (id INTEGER PRIMARY KEY, recipient VARCHAR(255),
                        amount DECIMAL(10, 2), date DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS
                       Expenses_Food_and_Drink (id INTEGER PRIMARY KEY,
                       recipient VARCHAR(255), amount DECIMAL(10, 2),
                       date DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Income
                        (id INTEGER PRIMARY KEY, payer VARCHAR(255),
                        amount DECIMAL(10, 2), date DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e


def menu():
    '''Home screen menu options'''

    print("\nWelcome to your expense and budget tracker.\n"
          "What would you like to do?\n"
          "\n1. Add expense"
          "\n2. View expenses"
          "\n3. View expenses by category"
          "\n4. Add income"
          "\n5. View income"
          "\n6. View income by category"
          "\n7. Set budget for a category"
          "\n8. View budget for a category"
          "\n9. Set financial goals"
          "\n10. View progress towards financial goals"
          "\n11. Quit")

    while True:
        try:
            menu_choice = int(input("\nMenu choice (1-11): "))
            if 1 <= menu_choice <= 11:
                options(menu_choice)
                break
            print("\nInvalid entry. Please enter a number between "
                  "1 and 11")
        except ValueError:
            print("\nInvalid entry. Please enter a number between 1 "
                  "and 11")


def options(menu_choice):
    '''
    Results from user's home menu choice

    :param menu_choice: The number chosen by the user at the home screen
    '''

    if menu_choice == 1:
        add_expense()
    if menu_choice == 2:
        view_expenses()
    if menu_choice == 11:
        print("\nYou have successfully quit the application!")
        exit()


def add_expense():
    '''Adds expense to the database'''

    while True:
        print("\nWhat category of expense is it?\n"
              "\n1. Bills"
              "\n2. Personal"
              "\n3. Travel"
              "\n4. Food and Drink"
              "\n5. Add new category")
        try:
            new_category = int(input("\nMenu choice (1-5): "))
            if not new_category:
                print("Category cannot be blank.")
                continue
            if new_category not in range(1, 6):
                print("\nInvalid entry. Please enter a number"
                      " between 1 and 5.")
                continue
            break
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue

    while True:
        new_recipient = input("\nWho is the recipient of the "
                              "expense?\n")
        if not new_recipient:
            print("Recipient cannot be blank.")
            continue

        while True:
            try:
                new_amount = float(input("\nWhat is the value of the "
                                         "expense?\n"))
                if new_amount < 0:
                    print("Amount cannot be negative.")
                    continue
                break
            except ValueError:
                print("\nInvalid entry. Please try again.")
                continue

        new_expense = Expense(None, new_recipient, new_amount,
                              today.isoformat())
        category = new_expense.add(new_category)

        print(f"\nNew expense added in {category}: "
              f"£{new_expense.amount:.2f} to {new_expense.recipient} "
              f"on {today}.")
        break

    add_more()


def add_more():
    '''Gives user option to add another expense'''

    while True:
        add_another = input("\nWould you like to add another expense?"
                            " (Y/N):\n")
        if add_another in ("Y", "y"):
            add_expense()
        if add_another in ("N", "n"):
            print("\nYou have chosen not to add any more expenses"
                  " and will be taken back to the home screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


def view_expenses():
    '''Gives user option to view, amend or delete expense'''

    print("\nWhat would you like to do?\n"
          "\n1. View all expenses"
          "\n2. Update an expense amount"
          "\n3. Delete an expense category")

    while True:
        try:
            view_option = int(input("\nMenu choice (1-3): "))
            if view_option not in range(1, 4):
                print("\nInvalid entry. Please enter a number between"
                      " 1 and 3.")
                continue
        except ValueError:
            print("\nInvalid entry. Please enter a number between 1 "
                  "and 3.")
            continue
        break


create_tables()
menu()
db.close()
