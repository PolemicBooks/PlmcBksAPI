import os

BASE_DIR = os.getcwd()

BOOKS_FILE = os.path.join(BASE_DIR, "files/books", "books.json")

ERRORS_FILE = os.path.join(BASE_DIR, "files/errors", "errors.json")

MESSAGES_FILE = os.path.join(BASE_DIR, "files/messages", "message_ids.json")

CATEGORIES_FILE = os.path.join(BASE_DIR, "files/books", "categories.json")
TYPES_FILE = os.path.join(BASE_DIR, "files/books", "types.json")
AUTHORS_FILE = os.path.join(BASE_DIR, "files/books", "authors.json")
NARRATORS_FILE = os.path.join(BASE_DIR, "files/books", "narrators.json")
PUBLISHERS_FILE = os.path.join(BASE_DIR, "files/books", "publishers.json")


BOT_TOKEN = ""
