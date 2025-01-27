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


class Transaction:
    '''Defining Transaction as its own class'''

    def __init__(self, transaction_id, recipient, amount,
                 transaction_type, transaction_date, category_id):
        self.transaction_id = transaction_id
        self.recipient = recipient
        self.amount = amount
        self.type = transaction_type
        self.transaction_date = transaction_date
        self.category_id = category_id

    def __str__(self):
        '''Returns transaction in easy-to-read string'''

        if self.type == "Expense":
            return (f"{self.amount:.2f} paid to {self.recipient}"
                    f" on {self.transaction_date}")
        if self.type == "Income":
            return (f"{self.amount:.2f} paid by {self.recipient}"
                    f" on {self.transaction_date}")

    def add(self, user_choice):
        '''Adds Transaction to Transactions table'''

        if user_choice in range(1, 5):
            category = user_choice
        else:
            category = self.category_id

        try:
            cursor.execute('''INSERT INTO Transactions
                           (recipient_or_payer, amount, type, date,
                           category_id) VALUES(?, ?, ?, ?, ?)''',
                           (self.recipient, self.amount, self.type,
                            self.transaction_date, category))
            db.commit()
        except sqlite3.Error as e:
            print("Error: The transaction could not be added. "
                  f"Error details: {e}")
            db.rollback()
            raise e

    def set_new_amount(self, new_amount, transaction_id):
        '''Changes amount value of Transaction'''

        try:
            cursor.execute('''UPDATE Transactions SET amount =
                           ? WHERE id = ?''', (new_amount,
                                               transaction_id))
            db.commit()
        except sqlite3.Error as e:
            print(f"Error: Amount could not be updated. Error details: "
                  f"{e}.")
            db.rollback()
            raise e


class Category:
    '''Defining Category as its own class'''

    def __init__(self, category_id, category_type):
        self.category_id = category_id
        self.category_type = category_type

    def add(self, category_name):
        '''Adds category to Categories tables'''

        try:
            cursor.execute('''INSERT INTO Categories
                          (category_type) VALUES(?)''',
                           (category_name,))
            db.commit()
        except sqlite3.Error as e:
            print("Error: The category could not be added. "
                  f"Error details: {e}")
            db.rollback()
            raise e


def create_tables():
    '''Creates tables for both transactions and categories'''

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Transactions
                        (id INTEGER PRIMARY KEY, recipient_or_payer
                       VARCHAR(255), amount DECIMAL(10, 2),
                       type VARCHAR(255), date DATE,
                       category_id INTEGER)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Categories
                        (category_id INTEGER PRIMARY KEY,
                         category_type VARCHAR(255))''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e


def add_default_category():
    '''Adds default categories to Category table'''

    # List of default categories to be added
    categories_to_add = [Category(1, "Bills"),
                         Category(2, "Personal"),
                         Category(3, "Travel"),
                         Category(4, "Food_and_Drink")]

    # Gets count from database to see if table needs populating
    try:
        cursor.execute('''SELECT COUNT(*) FROM Categories''')
        count = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error. Database could not be accessed.")
        raise e

    # Loops through list of categories and adds each one to database
    try:
        for category in categories_to_add:
            if count == 0:
                cursor.execute('''INSERT INTO Categories (category_id,
                               category_type) VALUES (?, ?)''',
                               (category.category_id,
                                category.category_type))
                db.commit()
    except sqlite3.Error as e:
        print("Error: Categories could not be added."
              f"Error details: {e}")
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
        define_category("Expense")
    if menu_choice == 2:
        view_expenses_menu()
    if menu_choice == 4:
        define_category("Income")
    if menu_choice == 11:
        print("\nYou have successfully quit the application!")
        exit()


def return_option():
    '''Gives user option to return to the main menu or quit'''

    print("Would you like to return to the main menu (R) or quit the "
          "application (Q)?")

    while True:
        return_or_quit = input("(R or Q):")
        if return_or_quit in ("R", "r"):
            menu()
        if return_or_quit in ("Q", "q"):
            print("\nYou have successfully quit the application!")
            exit()
        else:
            print("\nInvalid entry. Please try again.\n")
            continue


def define_category(transaction_type):
    '''Defines existing category or adds new category'''

    while True:
        print("\nWhat category of transaction is it?\n"
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

    if new_category == 5:
        while True:
            category_name = input("\nWhat would you like to call the "
                                  "new category?\n")
            if not category_name:
                print("Category name cannot be blank.")
                continue
            break

        new_category_type = Category(None, category_name)
        new_category_type.add(category_name)
        new_category_id = cursor.lastrowid
        add_transaction(new_category_id, new_category, category_name,
                        transaction_type)
    else:
        new_category_id = new_category
        add_transaction(new_category_id, new_category, None,
                        transaction_type)


def add_transaction(new_category_id, new_category, category_name,
                    transaction_type):
    '''Creates and adds a new transaction'''

    while True:
        new_recipient = input("\nWho is the recipient or payer of the "
                              "transaction?\n")
        if not new_recipient:
            print("Recipient cannot be blank.")
            continue

        while True:
            try:
                new_amount = float(input("\nWhat is the value of the "
                                         "transaction?\n"))
                if new_amount < 0:
                    print("Amount cannot be negative.")
                    continue
                break
            except ValueError:
                print("\nInvalid entry. Please try again.")
                continue

        new_transaction = Transaction(None, new_recipient, new_amount,
                                      transaction_type,
                                      today.isoformat(),
                                      new_category_id)

        category_map = {
            1: "Bills",
            2: "Personal",
            3: "Travel",
            4: "Food and Drink"}

        new_transaction.add(new_category_id)
        action_word = "to" if transaction_type == "Expense" else "from"

        if new_category in category_map:
            print(f"\nNew {transaction_type} added in "
                  f"{category_map[new_category]}: "
                  f"£{new_transaction.amount:.2f} {action_word} "
                  f"{new_transaction.recipient} on {today}.")

        if new_category == 5:
            print(f"\nNew {transaction_type} added in "
                  f"{category_name}: "
                  f"£{new_transaction.amount:.2f} {action_word} "
                  f"{new_transaction.recipient} on {today}.")
        break

    add_more(transaction_type)


def add_more(transaction_type):
    '''Gives user option to add another transaction'''

    while True:
        add_another = input("\nWould you like to add another "
                            "transaction? (Y/N):\n")
        if add_another in ("Y", "y"):
            define_category(transaction_type)
        if add_another in ("N", "n"):
            print("\nYou have chosen not to add any more transactions"
                  " and will be taken back to the home screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


def view_expenses_menu():
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

    if view_option == 1:
        view_all_transactions("Expense")
    if view_option == 2:
        update_amount("Expense")


def search_results(results, transaction_type):
    '''Iterates through search results'''

    for transaction in results:
        _, recipient, amount, _, transaction_date, \
            category_id = transaction
        transaction = Transaction(None, recipient, amount,
                                  transaction_type, transaction_date,
                                  category_id)
        print(transaction)
        print("\n")


def view_all_transactions(transaction_type):
    '''Displays all transactions in user-friendly way'''

    try:
        cursor.execute('''SELECT * FROM Transactions WHERE type = ?''',
                       (transaction_type,))
        transaction_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: The database could not be accessed. "
              f"Error details: {e}")
        raise e

    if not transaction_results:
        print("\nNo transactions found. Please try again.")
    else:
        print(f"\nAll {transaction_type} transactions:\n")

    search_results(transaction_results, transaction_type)
    return_option()


def update_amount(transaction_type):
    '''Updates amount of Expense or Income'''

    while True:
        try:
            id_to_update = int(input("\nEnter the transaction ID of the"
                                     " transaction you would like to "
                                     "update: "))
            if not id_to_update:
                print("\nID cannot be blank.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
        break

    try:
        cursor.execute('''SELECT * FROM Transactions WHERE id = ?
                       AND type = ?''', (id_to_update,
                                         transaction_type))
        update_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: The database could not be accessed. "
              f"Error details: {e}")
        raise e

    print("\nTransaction to update:")
    search_results(update_results, transaction_type)
    execute_update(id_to_update, transaction_type)


def execute_update(id_to_update, transaction_type):
    '''Carries out update of transaction amount'''

    transaction_to_update = Transaction(id_to_update, None,
                                        None, None, None, None)
    while True:
        try:
            updated_amount = float(input("What would you like to change"
                                         " the amount to?\n"))
            if not updated_amount:
                print("\nAmount cannot be blank.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
        break

    transaction_to_update.set_new_amount(updated_amount, id_to_update)
    print(f"\nAmount for transaction {id_to_update} updated to: "
          f"{updated_amount:.2f}.\n")

    update_more(transaction_type)


def update_more(transaction_type):
    '''Gives user option to update another transaction'''

    while True:
        update_another = input("\nWould you like to update another "
                               "transaction? (Y/N):\n")
        if update_another in ("Y", "y"):
            update_amount(transaction_type)
        if update_another in ("N", "n"):
            print("\nYou have chosen not to update any more "
                  "transactions and will be taken back to the home "
                  "screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


create_tables()
add_default_category()
menu()
db.close()
