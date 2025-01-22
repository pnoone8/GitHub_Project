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
                 transaction_date, category):
        self.transaction_id = transaction_id
        self.recipient = recipient
        self.amount = amount
        self.transaction_date = transaction_date
        self.category = category

    def add(self):
        '''Adds an expense to the database'''

        try:
            cursor.execute('''INSERT INTO expenses (recipient, amount,
                           date, category) VALUES(?, ?, ?, ?)''',
                           (self.recipient, self.amount,
                            self.transaction_date, self.category))
            db.commit()
        except sqlite3.Error as e:
            print("Error: The expense could not be added. "
                  f"Error details: {e}")
            db.rollback()
            raise e

    def set_category(self, user_choice):
        '''Sets category of expense based on user choice'''

        if user_choice == 1:
            self.category = "Bills"
        if user_choice == 2:
            self.category = "Personal"
        if user_choice == 3:
            self.category = "Travel"
        if user_choice == 4:
            self.category = "Food and drink"

        return self.category


class Income:
    '''Defining Income as its own class'''

    def __init__(self, transaction_id, payer, amount,
                 transaction_date, category):
        self.transaction_id = transaction_id
        self.payer = payer
        self.amount = amount
        self.transaction_date = transaction_date
        self.category = category


def create_tables():
    '''Creates tables for both expenses and income'''

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS expenses
                        (id INTEGER PRIMARY KEY, recipient VARCHAR(255),
                        amount DECIMAL(10, 2), date DATE,
                       category VARCHAR(255))''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS income
                        (id INTEGER PRIMARY KEY, payer VARCHAR(255),
                        amount DECIMAL(10, 2), date DATE,
                       category VARCHAR(255))''')
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
            print("\nInvalid choice. Please enter a number between "
                  "1 and 11")
        except ValueError:
            print("\nInvalid choice. Please enter a number between 1 "
                  "and 11")


def options(menu_choice):
    '''
    Results from user's home menu choice

    :param menu_choice: The number chosen by the user at the home screen
    '''

    if menu_choice == 1:
        add_expense()
    if menu_choice == 11:
        print("\nYou have successfully quit the application!")
        exit()


def add_expense():
    '''Adds expense to the database'''

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

        while True:
            print("\nWhat category of expense is it?\n"
                  "\n1. Bills"
                  "\n2. Personal"
                  "\n3. Travel"
                  "\n4. Food and drink")
            try:
                new_category = int(input("\nMenu choice (1-4): "))
                if not new_category:
                    print("Category cannot be blank.")
                    continue
                if new_category not in range(1, 5):
                    print("\nInvalid choice. Please enter a number"
                          " between 1 and 4.")
                    continue
                break
            except ValueError:
                print("\nInvalid entry. Please try again.")
                continue

        new_expense = Expense(None, new_recipient, new_amount,
                              today.isoformat(), new_category)
        new_expense.set_category(new_category)
        new_expense.add()
        print(f"\nNew expense added in {new_expense.category}: "
              f"£{new_expense.amount:.2f} to {new_expense.recipient} on"
              f" {today}.")
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


create_tables()
menu()
db.close()
