'''Module to access and edit database'''
import sqlite3
try:
    db = sqlite3.connect("./ebookstorev2.db")
    cursor = db.cursor()
except sqlite3.Error as e:
    print("Error: Could not connect to the database. "
          f"Error details: {e}.")
    raise e


class Book:
    '''Defining books as their own class'''

    def __init__(self, book_id, title, author, qty):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.qty = qty

    def __str__(self):
        '''Displays book info in easy-to-read string'''

        return (f"'{self.title}' by {self.author} currently has "
                f"{self.qty} copies in stock.")

    def does_exist(self, db_cursor):
        '''Updates book status when added to database'''

        db_cursor.execute('''SELECT COUNT(*) FROM book WHERE
                          LOWER(title) = LOWER(?) AND
                          LOWER(REPLACE(author, ".", "")) = LOWER(?)''',
                          (self.title, self.author))
        count = db_cursor.fetchone()
        return count[0] > 0

    def set_qty(self, db_cursor):
        '''Assigns qty to Book'''

        db_cursor.execute('''SELECT qty FROM book WHERE LOWER(title) =
                          LOWER(?) AND LOWER(REPLACE(author, ".", "")) =
                          LOWER(?)''', (self.title, self.author))
        qty = db_cursor.fetchone()
        self.qty = qty[0]

    def enter(self):
        '''Enters new book into the database'''

        try:
            cursor.execute('''INSERT INTO book (title, author, qty)
                           VALUES(?, ?, ?)''', (self.title, self.author,
                                                self.qty))
            db.commit()
        except sqlite3.Error as e:
            print("Error: The book could not be added. "
                  f"Error details: {e}")
            db.rollback()
            raise e

    def update_field(self, field, new_value, title_to_update,
                     author_to_update):
        '''Updates a specific field in the database'''

        try:
            cursor.execute(f'''UPDATE book SET {field} = ? WHERE
                            LOWER(title) = LOWER(?) AND
                            LOWER(REPLACE(author, ".", "")) =
                            LOWER(?)''', (new_value, title_to_update,
                                          author_to_update))
            db.commit()
        except sqlite3.Error as e:
            print(f"Error: Field could not be updated. Error details: "
                  f"{e}.")
            db.rollback()
            raise e

    def get_proper(self, user_title, user_author):
        '''Returns book author when searching for book'''

        cursor.execute('''SELECT title, author FROM book WHERE
                       LOWER(title) = LOWER(?) AND
                       LOWER(REPLACE(author, ".", "")) = LOWER(?)''',
                       (user_title, user_author))
        proper_title, proper_author = cursor.fetchone()
        return proper_title, proper_author

    def delete(self):
        '''Deletes book from the database'''

        try:
            cursor.execute('''DELETE FROM book WHERE
                            LOWER(title) = LOWER(?) AND
                            LOWER(REPLACE(author, ".", "")) =
                            LOWER(?)''', (self.title, self.author))
            db.commit()
        except sqlite3.Error as e:
            print(f"Error: Book could not be deleted. "
                  f"Error details: {e}.")
            db.rollback()
            raise e


def create_table():
    '''Creates and populates table when user first opens programme'''

    # This will only run when the table does not exist
    try:
        cursor.execute('''CREATE TABLE IF NOT EXISTS book
                        (id INTEGER PRIMARY KEY, title VARCHAR(255),
                        author VARCHAR(255), qty INTEGER)''')
        db.commit()
    except sqlite3.Error as e:
        print("Error: Table could not be created.")
        db.rollback()
        raise e


def insert_book():
    '''Inserts books into database'''

    # List of original books to be inserted
    books_to_add = [Book(3001, "A Tale of Two Cities",
                         "Charles Dickens", 30),
                    Book(3002, "Harry Potter and the Philosopher's "
                         "Stone", "J.K. Rowling", 40),
                    Book(3003, "The Lion, the Witch and the Wardrobe",
                         "C.S. Lewis", 25),
                    Book(3004, "The Lord of the Rings",
                         "J.R.R. Tolkien", 37),
                    Book(3005, "Alice in Wonderland", "Lewis Carroll",
                         12)]

    # Gets count from database to see if table needs populating
    try:
        cursor.execute('''SELECT COUNT(*) FROM book''')
        count = cursor.fetchone()[0]
    except sqlite3.Error as e:
        print("Error. Database could not be accessed.")
        raise e

    # Loops through list of books and adds each one to database
    try:
        for book in books_to_add:
            if count == 0:
                cursor.execute('''INSERT INTO book (id, title, author,
                               qty) VALUES (?, ?, ?, ?)''',
                               (book.book_id, book.title, book.author,
                                book.qty))
                db.commit()
    except sqlite3.Error as e:
        print("Error: Books could not be added."
              f"Error details: {e}")
        db.rollback()
        raise e


def menu():
    '''Options menu for the user upon startup'''

    while True:
        try:
            print(("-" * 26) + "\nWelcome to the bookstore.\n"
                  "What would you like to do?\n\n"
                  "1. Enter book\n"
                  "2. Update book\n"
                  "3. Delete book\n"
                  "4. Search books\n"
                  "0. Exit\n" +
                  ("-" * 26))

            menu_choice = int(input("Menu choice (0-4): "))

            if menu_choice == 1:
                enter_book()
            elif menu_choice == 2:
                update_book()
            elif menu_choice == 3:
                delete_book()
            elif menu_choice == 4:
                search_book()
            elif menu_choice == 0:
                print("Thanks for browsing the bookstore. "
                      "See you soon!")
                exit()
            else:
                print("\nInvalid selection. Please try again.")
        except ValueError:
            print("\nInvalid selection. Please try again.")
        except PermissionError:
            print("\nYou do not have permission to perform this "
                  "operation.")


def enter_book():
    '''Allows user to enter a book'''

    # Takes user values for title, author and qty
    while True:
        enter_title = input("\nWhat is the name of the book you would "
                            "like to enter?\n").strip()
        if not enter_title.strip():
            print("Book title cannot be empty. Please try again.")
            continue

        while True:
            enter_author = input("\nWho is the book by?\n").strip()
            if not enter_author.strip():
                print("Author cannot be empty. Please try again.")
                continue

            while True:
                try:
                    enter_qty = int(input("\nHow many copies are there "
                                          "in stock?\n"))
                    if enter_qty < 0:
                        print("\nQuantity cannot be negative. Please"
                              "re-enter.")
                        continue
                    break
                except ValueError:
                    print("\nInvalid entry. Please try again.")
                    continue
            break

        # Establishes user values as object in Book class
        new_book = Book(None, enter_title, enter_author, enter_qty)

        # Checks if book is already in database and notifies user if so
        if new_book.does_exist(cursor):
            not_summary = (f"\n'{new_book.title}' by {new_book.author} "
                           "could not be added because it is already "
                           "in the database.\n")
            print(("-" * len(not_summary)) + not_summary +
                  ("-" * len(not_summary)))
        else:
            # Enters book into database if no matching record found
            new_book.enter()
            new_summary = (f"\n'{new_book.title}' by {new_book.author} "
                           f"has been added to the system. There are "
                           f"{enter_qty} copies in stock.\n")
            print(("-" * len(new_summary)) + new_summary +
                  ("-" * len(new_summary)))
        enter_more()


def enter_more():
    '''Gives user opportunity to add another book after adding'''

    while True:
        add_another = input("\nWould you like to enter another book?"
                            " (Y/N):\n")
        if add_another in ("Y", "y"):
            enter_book()
        if add_another in ("N", "n"):
            print("\nYou have chosen not to add any more books and will"
                  " be taken back to the home screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


def update_book():
    '''Allows user to update specific details of a book'''

    while True:
        # User enters book they want to update
        title_to_update = input("\nEnter the title of the book you "
                                "would like to update:\n").strip()
        if not title_to_update.strip():
            print("Book title cannot be empty. Please try again.")
            continue

        while True:
            author_to_update = input("\nEnter the author of the book "
                                     "you would like to update:"
                                     "\n").strip()
            if not author_to_update.strip():
                print("Author cannot be empty. Please try again.")
                continue
            break

        # Updates qty with database value
        book_to_update.set_qty(cursor)

         # Establishes user choice as object in Book class
        book_to_update = Book(None, title_to_update, author_to_update,
                              None)

        if not book_to_update.does_exist(cursor):
            print(f"\n'{book_to_update.title} by "
                  f"{book_to_update.author} was not found in the "
                  "system. Please try again.")
            continue

        update_choice = get_update_choice()

        if update_choice == 1:
            update_book_title(book_to_update)
        elif update_choice == 2:
            update_book_author(book_to_update)
        elif update_choice == 3:
            update_book_qty(book_to_update)


def get_update_choice():
    '''User inputs which field to update'''

    while True:
        try:
            print(("-" * 31) +
                  "\nWhat would you like to update?\n"
                  "\n1. The book's title\n"
                  "2. The book's author\n"
                  "3. The book's stock quantity\n"
                  "0. Return to main menu\n"
                  + ("-" * 31))
            update_choice = int(input("Menu choice: (0-3): "))
            if update_choice in (1, 2, 3):
                return update_choice
            if update_choice == 0:
                menu()
            else:
                print("\nInvalid selection. Please try again:")
        except ValueError:
            print("\nInvalid selection. Please try again:")


def update_book_title(book_to_update):
    '''Updates title of a specific book'''

    # Notifies user of current book title
    proper_title, _ = book_to_update.get_proper(book_to_update.title,
                                                book_to_update.author)
    print(f"\nThe current title is '{proper_title}'.")

    # Updates title to user's chosen input
    while True:
        updated_title = input("\nWhat would you like to change the "
                              "title to?\n").strip()
        if not updated_title.strip():
            print("New title cannot be empty. Please try again.")
            continue
        break

    book_to_update.update_field('title', updated_title,
                                book_to_update.title,
                                book_to_update.author)

    title_summary = f"\nTitle changed to '{updated_title}'.\n"
    print(("-" * len(title_summary)) + title_summary +
          ("-" * len(title_summary)))

    update_more()


def update_book_author(book_to_update):
    '''Updates author of a specific book'''

    # Retrieves database title for display purposes
    proper_title, proper_author = \
        book_to_update.get_proper(book_to_update.title,
                                  book_to_update.author)
    print(f"\nThe current author is '{proper_author}'.")

    while True:
        updated_author = input("\nWhat would you like to change "
                               "the author to?\n").strip()
        if not updated_author.strip():
            print("New author cannot be empty. Please try again.")
            continue

        # Author updated as per user's input
        book_to_update.update_field('author', updated_author,
                                    book_to_update.title,
                                    book_to_update.author)
        author_summary = (f"\nAuthor of '{proper_title}' changed to "
                          f"{updated_author}.\n")
        print(("-" * len(author_summary)) + author_summary +
              ("-" * len(author_summary)))
        update_more()
        break


def update_book_qty(book_to_update):
    '''Updates quantity of a specific book'''

    # Retrieves database title for display purposes
    proper_title, proper_author = \
        book_to_update.get_proper(book_to_update.title,
                                  book_to_update.author)
    current_qty = book_to_update.qty

    # Notifies user of current quantity for chosen book
    print(f"\nThe current stock quantity of '{proper_title}' by "
          f"{proper_author} is {current_qty}.")

    while True:
        try:
            updated_qty = int(input("\nWhat would you like to change "
                                    f"the quantity of '{proper_title}' "
                                    f"by {proper_author} to?\n"))
            if updated_qty >= 0:
                book_to_update.update_field('qty', updated_qty,
                                            book_to_update.title,
                                            book_to_update.author)
                qty_summary = (f"\nStock quantity of '{proper_title}' "
                               f"by {proper_author} changed to "
                               f"{updated_qty}.\n")
                print(("-" * len(qty_summary)) + qty_summary +
                      ("-" * len(qty_summary)))
                update_more()
            else:
                print("\nQuantity cannot be negative. Please try "
                      "again.")
                continue
        except ValueError:
            print("\nInvalid selection. Please try again.")


def update_more():
    '''Gives user opportunity to update another book after updating'''

    while True:
        update_another = input("\nWould you like to update another "
                               "book? (Y/N):\n")
        if update_another in ("Y", "y"):
            update_book()
        if update_another in ("N", "n"):
            print("\nYou have chosen not to update any more books and "
                  "will be taken back to the home screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


def delete_book():
    '''Allows user to delete book of their choosing'''

    while True:
        # User enters book they want to delete
        title_to_delete = input("\nEnter the title of the book you "
                                "would like to delete:\n").strip()
        if not title_to_delete.strip():
            print("Book title cannot be empty. Please try again.")
            continue

        # Author provided as sanity check to ensure correct book
        while True:
            author_to_delete = input("\nEnter the author of the book "
                                     "you would like to delete:"
                                     "\n").strip()
            if not author_to_delete.strip():
                print("Author cannot be empty. Please try again.")
                continue
            break

        book_to_delete = Book(None, title_to_delete, author_to_delete,
                              None)

        # Checks if chosen book exists in the database
        if not book_to_delete.does_exist(cursor):
            print(f"\n'{book_to_delete.title}' by "
                  f"{book_to_delete.author} could not be found. Please "
                  "enter another title.")
            continue
        confirm_delete(book_to_delete)


def confirm_delete(book_to_delete):
    '''Gives user chance to confirm deletion or revert'''

    proper_title, proper_author = \
        book_to_delete.get_proper(book_to_delete.title,
                                  book_to_delete.author)

    while True:
        final_answer = input(f"\nYou are about to delete "
                             f"'{proper_title}' by "
                             f"{proper_author} from the"
                             f" system.\nAre you sure you want"
                             f" to do this? (Y/N)\n")
        if final_answer in ("Y", "y"):
            book_to_delete.delete()
            summary = (f"\n'{proper_title}' by {proper_author} has "
                       "been deleted from the system.\n")
            print(("-" * len(summary)) + summary + ("-" * len(summary)))
            delete_more()
            break
        if final_answer in ("N", "n"):
            print("\nNo books deleted.\nYou will be taken back to"
                  " the home screen.")
            menu()
            break
        print("\nInvalid entry. Please enter 'Y' or 'N'.")
    menu()


def delete_more():
    '''Gives user opportunity to delete another book after deleting'''

    while True:
        delete_another = input("\nWould you like to delete another "
                               "book? (Y/N):\n")
        if delete_another in ("Y", "y"):
            delete_book()
        if delete_another in ("N", "n"):
            print("\nYou have chosen not to delete any more books and "
                  "will be taken back to the home screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


def get_search_choice():
    '''User defines what they want to search for'''

    while True:
        try:
            print(("-" * 30) + "\nWelcome to the search "
                  "menu.\nWhat would you like to search for?\n"
                  "\n1. Books by title\n"
                  "2. Books by author\n"
                  "3. Low stock books\n"
                  "4. View complete inventory\n"
                  "0. Return to main menu\n" + ("-" * 30))
            search_choice = int(input("Menu choice (0-4): "))
            if search_choice in (1, 2, 3, 4):
                return search_choice
            if search_choice == 0:
                menu()
            else:
                print("\nInvalid entry. Please try again.\n")
        except ValueError:
            print("\nInvalid entry. Please try again.\n")


def search_results(results):
    '''Helper function to iterate through search results'''

    for book in results:
        title, author, qty = book
        book = Book(None, title, author, qty)
        print(book)
        print("\n")


def search_by_title():
    '''Search for books by title or keyword in title'''

    while True:
        search_title = input("\nSearch for a book title or a keyword "
                             "within a book title:\n")
        if not search_title:
            print("\nTitle cannot be empty. Please try again.")
            continue
        break

    # Returns all books containing user input in title
    try:
        cursor.execute('''SELECT title, author, qty FROM book WHERE
                        LOWER(title) LIKE LOWER(?) ORDER BY qty DESC''',
                       ("%" + search_title + "%",))
        title_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: Database could not be accessed. "
              f"Error details: {e}.")
        raise e

    # Error message if no books found
    if not title_results:
        print(f"\nNo books found containing '{search_title}'. "
              "Please try again.")
    else:
        print("\n" + ("-" * 69) +
              f"\nAll books containing '{search_title}':\n")

        # Establishes search results as Book objects & prints results
        search_results(title_results)
        print("-" * 69)
        search_more()


def search_by_author():
    '''Search for all books by a certain author'''

    # User inputs author's name
    while True:
        search_author = input("\nSearch for an author's "
                              "name:\n").strip()
        if not search_author.strip():
            print("Author cannot be empty. Please try again.")
            continue
        break

    # Normalised to handle full stops etc
    normalised_search_author = search_author.replace(".", "").lower()

    # Returns all titles by selected author
    try:
        cursor.execute('''SELECT title, author, qty FROM book WHERE
                        LOWER(REPLACE(author, ".", ""))
                        LIKE LOWER(?) ORDER BY qty DESC''',
                       ("%" + normalised_search_author + "%",))
        author_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: Database could not be accessed. "
              f"Error details: {e}.")
        raise e

    # Error messages for invalid inputs or if author not in database
    if not author_results:
        print(f"\nNo books by '{search_author}' found. "
              "Please try again.")
    else:
        # Establishes search results as Book objects & prints results
        print("\n" + ("-" * 69) +
              f"\nAll books by authors named '{search_author}':\n")
        search_results(author_results)
        print("-" * 69)
        search_more()


def search_by_low_stock():
    '''Search for books running low in stock'''

    # Returns all books with ten units or less in stock
    try:
        cursor.execute('''SELECT title, author, qty FROM book WHERE
                   qty <= 10 ORDER BY qty DESC''')
        low_stock_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: Database could not be accessed. "
              f"Error details: {e}")
        raise e

    # Displays low stock items to the user
    if not low_stock_results:
        print("\n" + ("-" * 26) + "\nThere are currently no books "
              "running low in stock.\n")
        search_more()
    else:
        print("\n" + ("-" * 52) + "\nWe are running low in stock of "
              "the following books:\n")
        search_results(low_stock_results)
        print("-" * 52)
        search_more()


def search_all_stock():
    '''Search all books currently in stock'''

    # Returns all books in stock (NB: excludes books in db with 0 stock)
    try:
        cursor.execute('''SELECT title, author, qty FROM book WHERE qty
                       > 0 ORDER BY qty DESC''')
        all_results = cursor.fetchall()
    except sqlite3.Error as e:
        print("Error: Database could not be accessed. "
              f"Error details: {e}")
        raise e

    # Error messages for invalid inputs; displays all stock for user
    if not all_results:
        print("\nThere are currently no books in the database.")
    else:
        print("\n" + ("-" * 69) + "\nCurrent Inventory:\n")
        search_results(all_results)
        print("-" * 69)
        search_more()


def search_book():
    '''Allows user to search db for books by title, author or qty'''

    user_search = get_search_choice()

    while True:
        if user_search == 1:
            search_by_title()
        elif user_search == 2:
            search_by_author()
        elif user_search == 3:
            search_by_low_stock()
        elif user_search == 4:
            search_all_stock()


def search_more():
    '''Gives user opportunity to search another book after searching'''

    while True:
        search_another = input("\nWould you like to do another search?"
                               " (Y/N):\n")
        if search_another in ("Y", "y"):
            search_book()
        if search_another in ("N", "n"):
            print("\nYou have chosen not to search for any more books "
                  "and will be taken back to the home screen.\n")
            menu()
        else:
            print("\nInvalid entry. Please enter 'Y' or 'N'.")
            continue


create_table()
insert_book()
menu()
db.close()
