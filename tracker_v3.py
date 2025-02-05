# pylint: disable=R0915
'''
Importing SQL module to access and edit database.
Also importing date info for tagging later in the program.
'''

import sqlite3
from datetime import date, datetime

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
BREAK_MARKER = "-" * 44


class Transaction:
    '''Class to represent Transactions, both Expenses and Incomes.

    Attributes:
        transaction_id (int): Unique transaction identifier.
        recipient (str): Name of recipient (for Expense) or payer
                         (for Income).
        amount (float): Transaction amount.
        transaction_date (date): Date of transaction.
        type (str): 'Expense' or 'Income'.
        category_id (int): ID of the associated category.
    '''

    def __init__(self, transaction_id, recipient, amount,
                 transaction_type, transaction_date, category_id):
        '''Set up parameters for Transaction objects.'''
        self.transaction_id = transaction_id
        self.recipient = recipient
        self.amount = amount
        self.type = transaction_type
        self.transaction_date = transaction_date
        self.category_id = category_id

    def __str__(self):
        '''Return Transaction in easy-to-read string.'''
        action_word = "to" if self.type == "Expense" else "by"

        return (f"£{self.amount:.2f} {action_word} "
                f"{self.recipient} on {self.transaction_date}.")

    def add(self, user_choice):
        '''Add Transaction to Transactions table.'''

        # Adds chosen category if user chooses from default list
        if user_choice > 0:
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
        '''Change amount value of Transaction.'''
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

    def category_to_null(self, deleted_category_id):
        '''Set category_id to NULL once category has been deleted.'''
        try:
            cursor.execute('''UPDATE Transactions SET category_id =
                           ? WHERE category_id = ?''',
                           (None, deleted_category_id))
            db.commit()
        except sqlite3.Error as e:
            print(f"Error: Transaction could not be updated. "
                  f"Error details: {e}.")
            db.rollback()
            raise e


class Category:
    '''Define Category as its own class.

    Attributes:
        category_id(int): Unique category identifier that corresponds to
                          user inputs
        category_type(str): Name of Transaction category
    '''

    def __init__(self, category_id, category_type):
        '''Set up parameters for Category objects.'''
        self.category_id = category_id
        self.category_type = category_type

    def add(self, category_name):
        '''Add new Category to Categories tables.'''
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

    def does_exist(self, db_cursor):
        '''Check if a Category exists when user tries to add.'''
        try:
            db_cursor.execute('''SELECT COUNT(*) FROM Categories WHERE
                            LOWER(category_type) = LOWER(?)''',
                              (self.category_type,))
            count = db_cursor.fetchone()
        except sqlite3.Error as e:
            print("Error: The database could not be accessed. "
                  f"Error details: {e}")
            raise e

        return count[0] > 0

    def delete(self):
        '''Delete a Category from the database.'''
        try:
            cursor.execute('''DELETE FROM Categories WHERE
                            category_id = ?''',
                           (self.category_id,))
            db.commit()
        except sqlite3.Error as e:
            print(f"Error: Category could not be deleted. "
                  f"Error details: {e}.")
            db.rollback()
            raise e


class Budget:
    '''Define Budget as its own class.

    Attributes:
        budget_id (int): Unique Budget identifier.
        category_id (int): ID of the associated category.
        budget_amount (float): Budget amount.
        start_date (date): Start date of Budget period.
        end_date (date): End date of Budget period.
    '''

    def __init__(self, budget_id, category_id, budget_amount,
                 start_date, end_date):
        '''Set up parameters for Budget object'''
        self.budget_id = budget_id
        self.category_id = category_id
        self.budget_amount = budget_amount
        self.start_date = start_date
        self.end_date = end_date

    def __str__(self):
        '''Return Budget in user-friendly format.'''
        return (f"£{self.budget_amount:.2f} for period "
                f"{self.start_date} to {self.end_date}.")

    def add(self):
        '''Add Budget to the Budgets table.'''
        try:
            cursor.execute('''INSERT INTO Budgets (category_id,
                           budget_amount, start, end)
                           VALUES(?, ?, ?, ?)''',
                           (self.category_id, self.budget_amount,
                            self.start_date, self.end_date))
            db.commit()
        except sqlite3.Error as e:
            print("Error: The category could not be added. "
                  f"Error details: {e}")
            db.rollback()
            raise e

        category_map = get_category_map()
        print(f"\n{category_map[self.category_id]} Budget set: "
              f"£{self.budget_amount:.2f} for period {self.start_date} "
              f"to {self.end_date}.")


class Goal:
    '''Define Goal as its own class.

    Attributes:
        goal_id (int): Unique Goal identifier.
        category_id (int): ID of the associated category.
        goal_target (float): Amount to target in specified category.
        due_date (date): Date by which Goal should be reached.
    '''

    def __init__(self, goal_id, category_id, goal_target, due_date):
        self.goal_id = goal_id
        self.category_id = category_id
        self.goal_target = goal_target
        self.due_date = due_date

    def __str__(self):
        '''Returns Goal in a user-friendly format.'''
        category_map = get_category_map()
        return (f"Achieve £{self.goal_target:.2f} in "
                f"{category_map[self.category_id]} by {self.due_date}.")

    def add(self):
        '''Adds Goal to the Goals table.'''
        try:
            cursor.execute('''INSERT INTO Goals (goal_id, category_id,
                           goal_target, due_date) VALUES(?, ?, ?, ?)''',
                           (self.goal_id, self.category_id,
                            self.goal_target,
                            self.due_date.isoformat()))
            db.commit()
        except sqlite3.Error as e:
            print("Error: The category could not be added. "
                  f"Error details: {e}")
            db.rollback()
            raise e

    def progress(self, progress_choice):
        '''Calcuates progress towards Goal.'''
        category_map = get_category_map()

        try:
            # Get total income in a Category from database
            cursor.execute('''SELECT sum(amount) FROM Transactions
                           WHERE type = ? AND category_id = ?''',
                           ("Income", progress_choice))
            category_income = cursor.fetchone()[0] or 0

            # Get total expenses in a Category from database
            cursor.execute('''SELECT sum(amount) FROM Transactions
                           WHERE type = ? AND category_id = ?''',
                           ("Expense", progress_choice))
            category_expense = cursor.fetchone()[0] or 0

            if category_income == 0 and category_expense == 0:
                return ("No transactions were found in "
                        f"{category_map[progress_choice]}.")

            # Calculate total towards progress
            progress_total = category_income - category_expense

            # Recast date to date format
            due_date = datetime.strptime(self.due_date,
                                         "%Y-%m-%d").date()

            # Display messages to user notifying them of progress
            if progress_total >= 0:
                progress_percent = (progress_total /
                                    self.goal_target) * 100
                if progress_percent < 100:
                    return (f"You are {progress_percent:.0f}% of "
                            "the way to achieving your "
                            f"{category_map[progress_choice]} Goal and"
                            f" you have {(due_date - today).days} days "
                            "left.")
                else:
                    return ("You have achieved your "
                            f"{category_map[progress_choice]} Goal!")
            else:
                goal_deficit = abs(progress_total - self.goal_target)
                return (f"You are £{goal_deficit:.2f} away from "
                        f"reaching your {category_map[progress_choice]}"
                        f" Goal and you have {(due_date - today).days}"
                        " days left.")

        except sqlite3.Error as e:
            return ("Error: The database could not be accessed. "
                    f"Error details: {e}")


def create_tables():
    '''Create tables for Transactions, Categories, Budgets and Goals.'''
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

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Budgets
                        (budget_id INTEGER PRIMARY KEY,
                       category_id INTEGER, budget_amount
                       DECIMAL(10, 2), start DATE, end DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e

    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS Goals
                        (goal_id INTEGER PRIMARY KEY,
                       category_id INTEGER, goal_target DECIMAL(10, 2),
                       due_date DATE)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e


def add_default_category():
    '''Add default categories to Category table.'''

    # List of default categories to be added
    categories_to_add = [Category(1, "Bills"),
                         Category(2, "Personal"),
                         Category(3, "Travel"),
                         Category(4, "Food")]

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


def get_category_map():
    '''Create dynamic category map based on user's adds and deletes.'''
    category_map = {}

    try:
        cursor.execute('''SELECT category_id, category_type FROM
                       Categories''')
        for category_id, category_type in cursor.fetchall():
            category_map[category_id] = category_type
    except sqlite3.Error as e:
        print(f"Error fetching categories: {e}")

    return category_map


def print_category_map(category_map):
    '''Helper function to print category map when needed.'''
    for key, value in category_map.items():
        print(f"{key}. {value}")


def menu():
    '''Home screen menu options.'''
    print("\nWelcome to your Expense and Budget Tracker."
          f"\n{BREAK_MARKER}\n"
          "Please select an option from the menu below:\n"
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
            print(BREAK_MARKER)
            if 1 <= menu_choice <= 11:
                options(menu_choice)
                break
            print("\nInvalid entry. Please enter a number between "
                  "1 and 11")
        except ValueError:
            print("\nInvalid entry. Please enter a number between 1 "
                  "and 11")


def options(menu_choice):
    '''Results from user's home menu choice.'''
    if menu_choice == 1:
        define_category("Expense")
    if menu_choice == 2:
        view_transaction_menu("Expense")
    if menu_choice == 3:
        transaction_by_category("Expense")
    if menu_choice == 4:
        define_category("Income")
    if menu_choice == 5:
        view_transaction_menu("Income")
    if menu_choice == 6:
        transaction_by_category("Income")
    if menu_choice == 7:
        set_category("Budget")
    if menu_choice == 8:
        budget_by_category()
    if menu_choice == 9:
        set_category("Goal")
    if menu_choice == 10:
        view_progress()
    if menu_choice == 11:
        print("\nYou have successfully quit the application!\n")
        exit()


def define_category(transaction_type):
    '''Define existing Category or add new Category.'''

    # Gives user the option of choosing a default category or adding new
    while True:
        category_map = get_category_map()
        print(f"\nWhat category of {transaction_type} is it?\n")
        print_category_map(category_map)
        print("0. Add new category")

        try:
            new_category = int(input("\nMenu choice: "))
            print(BREAK_MARKER)
            if new_category not in category_map and new_category != 0:
                print("\nInvalid entry. Please try again.")
                continue
            break
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue

    add_category(new_category, transaction_type)


def add_category(new_category, transaction_type):
    '''Add new category.'''

    # User chooses new category name
    if new_category == 0:
        while True:
            category_name = input("\nWhat would you like to call the "
                                  "new category?\n")
            if not category_name:
                print("Category name cannot be blank.")
                continue

            # Creates new category as object in Category class
            new_category_type = Category(None, category_name)

            # Checks if new category exists in database, adds if not
            if new_category_type.does_exist(cursor):
                print(f"\n{new_category_type.category_type} category "
                      "could not be added because it already exists.")
                continue
            new_category_type.add(category_name)
            break

        # Adding new category to category map
        category_map = get_category_map()
        new_key = max(category_map.keys()) + 1
        category_map[new_key] = category_name

        # Assigns category id to object
        new_category_id = cursor.lastrowid
        add_transaction(new_category_id, new_category, category_name,
                        transaction_type)
    else:
        new_category_id = new_category
        add_transaction(new_category_id, new_category, None,
                        transaction_type)


def add_transaction(new_category_id, new_category, category_name,
                    transaction_type):
    '''Create and add a new transaction.'''
    while True:
        person_word = "recipient" if transaction_type == \
            "Expense" else "payer"
        new_recipient = input(f"\nWho is the {person_word} of the "
                              f"{transaction_type}?\n")
        if not new_recipient:
            print("Recipient cannot be blank.")
            continue

        while True:
            try:
                new_amount = float(input("\nWhat is the value of the "
                                         f"{transaction_type}?\n"))
                if new_amount < 0:
                    print("Amount cannot be negative.")
                    continue
                break
            except ValueError:
                print("\nInvalid entry. Please try again.")
                continue
        # Creates new object in Transaction class from user inputs
        new_transaction = Transaction(None, new_recipient, new_amount,
                                      transaction_type,
                                      today.isoformat(),
                                      new_category_id)
        # Adds new transaction to database
        new_transaction.add(new_category_id)
        budget_notice(transaction_type, new_category_id)

        category_map = get_category_map()
        if new_category in category_map:
            print(f"\nNew {transaction_type} added in "
                  f"{category_map[new_category]}: {new_transaction}")

        if new_category == 0:
            print(f"\nNew {transaction_type} added in {category_name}: "
                  f"{new_transaction}")

        print(BREAK_MARKER)
        break

    more(transaction_type, "add", transaction_type)


def budget_notice(transaction_type, category_id):
    '''Update user on spending or income.'''
    try:
        cursor.execute('''SELECT sum(amount) FROM Transactions WHERE
                       type = ? AND category_id = ?''',
                       (transaction_type, category_id))
        transaction_sum = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error: Database could not be accessed."
              f"Error details: {e}")

    try:
        cursor.execute('''SELECT sum(budget_amount) FROM Budgets WHERE
                       category_id = ?''', (category_id,))
        budget_sum = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error: Database could not be accessed."
              f"Error details: {e}")

    category_map = get_category_map()

    # Warning message if user is approaching Budget total
    if budget_sum:
        if (transaction_type == "Expense" and
                transaction_sum > (budget_sum * 0.9)):
            print("\n***WARNING*** You have spent more than 90% of "
                  f"your {category_map[category_id]} Budget.")
        elif (transaction_type == "Income" and
              transaction_sum > (budget_sum * 0.9)):
            print("\nYou have received more than 90% of your "
                  f"{category_map[category_id]} Budget.")


def more(transaction_type, verb, noun):
    '''Give user option to repeat current function.'''
    while True:
        repeat_action = input(f"\nWould you like to {verb} another "
                              f"{transaction_type}? (Y/N):\n")
        if repeat_action in ("Y", "y"):
            if verb == "add":
                define_category(transaction_type)
            elif verb == "update":
                update_amount(transaction_type)
            elif verb == "delete":
                delete_category()
            elif verb == "set" and noun == "Budget":
                set_category("Budget")
            elif verb == "set" and noun == "Goal":
                set_category("Goal")
            elif verb == "view" and noun == "transaction":
                view_transaction_menu(transaction_type)
            elif verb == "view" and noun == "target":
                view_progress()
            elif verb == "view" and noun == "category":
                transaction_by_category(transaction_type)
            elif verb == "view" and noun == "Budget categorie":
                budget_by_category()
        if repeat_action in ("N", "n"):
            print(f"\nYou have chosen not to {verb} any more {noun}s"
                  " and will be taken back to the home screen.\n")
            print(BREAK_MARKER)
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


def view_transaction_menu(transaction_type):
    '''Give user option to view, amend or delete transaction.'''
    print("\nWhat would you like to do?\n"
          f"\n1. View all {transaction_type} transactions"
          f"\n2. Update an {transaction_type} amount"
          f"\n3. Delete an {transaction_type} category")

    while True:
        try:
            view_option = int(input("\nMenu choice (1-3): "))
            print(BREAK_MARKER)
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
        view_all_transactions(transaction_type)
    if view_option == 2:
        update_amount(transaction_type)
    if view_option == 3:
        delete_category()


def search_results(results, table_name):
    '''Iterate through search results in different classes.'''
    transactions = []
    budgets = []
    goals = []

    if table_name == "Transactions":
        for transaction in results:
            _, recipient, amount, transaction_type, transaction_date, \
                category_id = transaction
            transaction = Transaction(None, recipient, amount,
                                      transaction_type,
                                      transaction_date, category_id)
            transactions.append(transaction)
        return transactions

    if table_name == "Budgets":
        for budget in results:
            _, category_id, budget_amount, start, end = budget
            budget = Budget(None, category_id, budget_amount, start,
                            end)
            budgets.append(budget)
        return budgets

    if table_name == "Goals":
        for goal in results:
            _, category_id, goal_target, due_date = goal
            goal = Goal(None, category_id, goal_target, due_date)
            goals.append(goal)
        return goals

    else:
        raise ValueError("\nInvalid table name.")


def print_results(results, table_name, category_id):
    '''Helper function to print results after search.'''
    if table_name == "Transactions":
        results = search_results(results, "Transactions")
        for transaction in results:
            print(f"{transaction}\n")

    elif table_name == "Budgets":
        results = search_results(results, "Budgets")
        for budget in results:
            print(f"{budget}\n")

    elif table_name == "Goals":
        results = search_results(results, "Goals")
        for goal in results:
            progress_message = goal.progress(category_id)
            print(f"{goal} {progress_message}\n")

    else:
        raise ValueError("\nInvalid table name.")


def view_all_transactions(transaction_type):
    '''Display all transactions in user-friendly way.'''
    try:
        cursor.execute('''SELECT * FROM Transactions WHERE type = ?''',
                       (transaction_type,))
        transaction_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: The database could not be accessed. "
              f"Error details: {e}")
        raise e

    if not transaction_results:
        print("\nNo transactions found. Please try again.\n")
    else:
        print(f"\nAll {transaction_type} transactions:\n")
        print_results(transaction_results, "Transactions", None)

    print(BREAK_MARKER)

    more(transaction_type, "view", "transaction")


def update_amount(transaction_type):
    '''Update amount of Expense or Income Transaction.'''
    while True:
        try:
            id_to_update = int(input("\nEnter the transaction ID of the"
                                     " transaction you would like to "
                                     "update:\n"))
            if id_to_update <= 0:
                print("\nID must be a positive number.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue

        try:
            cursor.execute('''SELECT id FROM Transactions where type
                           = ?''', (transaction_type,))
            id_list = cursor.fetchall()

            if (id_to_update,) in id_list:
                cursor.execute('''SELECT * FROM Transactions WHERE id
                               = ? AND type = ?''',
                               (id_to_update, transaction_type))
                update_results = cursor.fetchall()
                print("\nTransaction to update:")
                print_results(update_results, "Transactions", None)
            else:
                print("\nTransaction ID not found in "
                      f"{transaction_type}s. Please try again.")
                continue
        except sqlite3.Error as e:
            print("Error: The database could not be accessed. "
                  f"Error details: {e}")
            raise e
        break

    execute_update(id_to_update, transaction_type)


def execute_update(id_to_update, transaction_type):
    '''Carry out update of transaction amount.'''
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
    budget_notice(transaction_type, id_to_update)
    print(f"\nAmount for transaction {id_to_update} updated to: "
          f"£{updated_amount:.2f}.\n")
    print(BREAK_MARKER)

    more(transaction_type, "update", transaction_type)


def delete_category():
    '''Delete a Category from the database.'''

    # User selects which Category to delete
    while True:
        category_map = get_category_map()
        print("\nWhich category would you like to delete?\n")
        print_category_map(category_map)

        try:
            delete_choice = int(input("\nMenu choice: "))
            if delete_choice not in category_map:
                print("\nInvalid entry. Please try again.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue

        # Accesses Category from category map
        category_type = category_map.get(delete_choice)

        # Assigns chosen Category to Category class
        category_to_delete = Category(delete_choice, category_type)

        if not category_to_delete.does_exist(cursor):
            print(f"\n{category_to_delete.category_type} "
                  "could not be deleted because it does not exist.")
            continue
        category_to_delete.delete()
        print(f"\n{category_to_delete.category_type} was deleted "
              "from the database.")
        break

    print(BREAK_MARKER)
    null_deleted_category(delete_choice)
    more("Category", "delete", "Categorie")


def null_deleted_category(delete_choice):
    '''Change category_id to NULL after Category deleted.'''
    try:
        # Selects all Transactions in deleted category
        cursor.execute('''SELECT * FROM Transactions WHERE
                       category_id = ?''', (delete_choice,))
        transactions = cursor.fetchall()

        results = search_results(transactions, "Transactions")

        # Redefines category as NULL
        for transaction in results:
            transaction.category_to_null(delete_choice)
    except sqlite3.Error as e:
        print("Error: The database could not be accessed. "
              f"Error details: {e}")
        raise e


def transaction_by_category(transaction_type):
    '''Allow user to view Transactions by Category.'''
    while True:
        try:
            category_map = get_category_map()
            print(f"\nWhich category of {transaction_type} would you "
                  "like to view?\n")
            print_category_map(category_map)
            category_choice = int(input("\nMenu choice: "))
            print(BREAK_MARKER)
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue

        if category_choice in category_map:
            try:
                cursor.execute('''SELECT * FROM Transactions WHERE
                               type = ? AND category_id = ?''',
                               (transaction_type, category_choice,))
                transactions = cursor.fetchall()
            except sqlite3.Error as e:
                print("Error: The database could not be accessed. "
                      f"Error details: {e}")
                raise e
        else:
            print("\nCategory not found. Please try again.")
            continue

        if not transactions:
            print(f"\nNo {transaction_type} transactions found in"
                  f" {category_map[category_choice]}.\n")
        else:
            print(f"\nAll {transaction_type} transactions in "
                  f"{category_map[category_choice]}:\n")
            print_results(transactions, "Transactions", None)
        break

    print(BREAK_MARKER)
    more(transaction_type, "view", "category")


def set_category(user_class):
    '''Set Budget or Goal by Category.'''
    while True:
        try:
            category_map = get_category_map()
            print(f"\nWhich category would you like to set a "
                  f"{user_class} for?\n")
            print_category_map(category_map)
            class_category = int(input("\nMenu choice: "))
            print(BREAK_MARKER)
            if class_category not in category_map:
                print("\nCategory not found. Please try again.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue
        break

    if user_class == "Budget":
        set_amount(class_category, "Budget amount", user_class)
    if user_class == "Goal":
        set_amount(class_category, "Goal target", user_class)


def set_amount(class_category, class_name, user_class):
    '''Set amount for new Budget.'''
    while True:
        try:
            new_amount = float(input("\nWhat would you like to set "
                                     f"the {class_name} to?\n"))
            if new_amount < 0:
                print("\nAmount must be positive.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue
        break

    if user_class == "Budget":
        set_budget_time(class_category, new_amount)
    if user_class == "Goal":
        set_goal_due_date(class_category, new_amount)


def set_budget_time(class_category, new_amount):
    '''Set time period for new Budget.'''
    while True:
        try:
            user_start = input("\nWhat is the start date for the "
                               "Budget? (YYYY-MM-DD)\n")
            start_date = datetime.strptime(user_start, "%Y-%m-%d").\
                date().isoformat()
        except ValueError:
            print("\nInvalid date format. Please use "
                  "YYYY-MM-DD")
            continue

        while True:
            try:
                user_end = input("\nWhat is the end date for the "
                                 "Budget? (YYYY-MM-DD)\n")
                end_date = datetime.strptime(user_end, "%Y-%m-%d").\
                    date().isoformat()
                if end_date < start_date:
                    print("\nEnd date cannot be before start"
                          " date.")
                    continue
            except ValueError:
                print("\nInvalid date format. Please use "
                      "YYYY-MM-DD")
                continue
            break

        enter_budget(class_category, new_amount, start_date,
                     end_date)


def enter_budget(budget_category, budget_amount, start_date, end_date):
    '''Enter Category Budget into database.'''
    new_budget = Budget(None, budget_category, budget_amount,
                        start_date, end_date)
    new_budget.add()

    print(BREAK_MARKER)
    more("Budget", "set", "Budget")


def budget_by_category():
    '''Allow user to view Budgets by Category.'''
    while True:
        try:
            category_map = get_category_map()
            print("\nWhich category of Budget would you like to "
                  "view?\n")
            print_category_map(category_map)
            category_choice = int(input("\nMenu choice: "))
            print(BREAK_MARKER)
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue

        if category_choice in category_map:
            try:
                cursor.execute('''SELECT * FROM Budgets WHERE
                               category_id = ?''', (category_choice,))
                budgets = cursor.fetchall()
            except sqlite3.Error as e:
                print("Error: The database could not be accessed. "
                      f"Error details: {e}")
                raise e
        else:
            print("\nCategory not found. Please try again.")
            continue

        if not budgets:
            print(f"\nNo Budgets found in"
                  f" {category_map[category_choice]}.\n")
        else:
            print(f"\n{category_map[category_choice]} Budget:\n")
            print_results(budgets, "Budgets", None)
            print(BREAK_MARKER)
        break

    more("Budget category", "view", "Budget categorie")


def set_goal_due_date(class_category, new_amount):
    '''Set due date for financial Goal.'''
    while True:
        try:
            target_date = input("\nWhat date should the Goal be "
                                "achieved by? (YYYY-MM-DD)\n")
            due_date = datetime.strptime(target_date, "%Y-%m-%d").\
                date()
            if due_date < today:
                print("\nDue date cannot be in the past.")
                continue
        except ValueError:
            print("\nInvalid date format. Please use "
                  "YYYY-MM-DD")
            continue
        break

    enter_goal(class_category, new_amount, due_date)


def enter_goal(class_category, new_amount, due_date):
    '''Enter Goal into the database.'''
    new_goal = Goal(None, class_category, new_amount, due_date)
    new_goal.add()

    print(f"\nGoal added: {new_goal}")
    more("Goal", "set", "Goal")


def view_progress():
    '''View progress towards financial Goals.'''
    while True:
        try:
            category_map = get_category_map()
            print("\nWhich category's progress would you like to "
                  "view?\n")
            print_category_map(category_map)
            progress_choice = int(input("\nMenu choice: "))
            print(BREAK_MARKER)
            if progress_choice not in category_map:
                print("\nInvalid entry. Please try again.")
                continue
        except ValueError:
            print("\nInvalid entry. Please try again.")
            continue
        break

    display_progress(progress_choice, category_map)


def display_progress(progress_choice, category_map):
    '''Display Goal progress to user.'''
    try:
        cursor.execute('''SELECT * FROM Goals WHERE category_id = ?''',
                       (progress_choice,))
        results = cursor.fetchall()
        if not results:
            print(f"\nNo Goals set in {category_map[progress_choice]}.")
        else:
            print(f"\nAll Goals in {category_map[progress_choice]}:\n")
            print_results(results, "Goals", progress_choice)
            print(BREAK_MARKER)
    except sqlite3.Error as e:
        print("Error: The database could not be accessed. "
              f"Error details: {e}")
        raise e

    more("target", "view", "target")


create_tables()
add_default_category()
menu()
db.close()
