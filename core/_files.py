import json

from ._config import (
	BOOKS_FILE,
	ERRORS_FILE,
	MESSAGES_FILE,
	CATEGORIES_FILE,
	TYPES_FILE,
	AUTHORS_FILE,
	NARRATORS_FILE,
	PUBLISHERS_FILE
)

with open(file=BOOKS_FILE, mode="r") as file:
	books = json.loads(file.read())

with open(file=ERRORS_FILE, mode="r") as file:
	errors = json.loads(file.read())

with open(file=MESSAGES_FILE, mode="r") as file:
	messages = json.loads(file.read())

with open(file=CATEGORIES_FILE, mode="r") as file:
	categories = json.loads(file.read())

with open(file=TYPES_FILE, mode="r") as file:
	types = json.loads(file.read())

with open(file=AUTHORS_FILE, mode="r") as file:
	authors = json.loads(file.read())

with open(file=NARRATORS_FILE, mode="r") as file:
	narrators = json.loads(file.read())

with open(file=PUBLISHERS_FILE, mode="r") as file:
	publishers = json.loads(file.read())

