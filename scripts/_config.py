import os

BASE_DIR = os.path.dirname(os.getcwd())

MESSAGES_DIRECTORY = os.path.join(BASE_DIR, "files/messages")

BOOKS_DIRECTORY = os.path.join(BASE_DIR, "files/books")

DUMPS_DIRECTORY = os.path.join(BASE_DIR, "files/dumps")

PYROGRAM_OPTIONS = {
	"session_name": "bot",
	"api_id": "",
	"api_hash": "",
	"bot_token": "",
	"workdir": os.path.join(BASE_DIR, "files/pyrogram"),
	"parse_mode": "markdown",
}

