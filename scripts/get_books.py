import json
import time

import pandas
from pyrogram import Client
from unidecode import unidecode

from _config import *
from _core import *
from _utils import *

books = []

message_id = 0

message_ids = []

files_info = []

book = {}

client = Client(**PYROGRAM_OPTIONS)
client.start()

while message_id < 135000:
	
	message_id += 1
	
	# Essas mensagens não são publicações de livros
	if message_id in (2, 10596, 10597, 13337, 131117):
		continue
	
	message = client.get_messages("@PolemicBooks", message_id)
	
	if message.empty or message.service:
		continue
	
	message_ids.append(message_id)
	
	if message.photo and message.caption:
		if book:
			books.append(book)
		
		book_title = message.caption.split(sep="\n")[0]
		
		author, publisher, book_type, category, narrator, duration = (
			get_author(message.caption.markdown),
			get_publisher(message.caption.markdown),
			get_book_type(message.caption.markdown),
			get_category(message.caption.markdown),
			get_narrator(message.caption.markdown),
			get_duration(message.caption.markdown),
		)
		
		book = {
			"id": message.message_id,
			"title": None if book_title is None else capitalize_words(book_title),
			"title_ascii_lower": None if book_title is None else capitalize_words(unidecode(book_title)).lower(),
			"type": book_type,
			"category": None if category is None else category.replace("\\", "/"),
			"duration": {
				"seconds": human_duration_to_seconds(message.caption.markdown) if book_type == "Audiobook" else None,
				"human": duration
			},
			"size": {
				"bytes": 0,
				"human": None
			},
			"author": None if author is None else capitalize_words(author),
			"narrator": None if narrator is None else capitalize_words(narrator),
			"publisher": None if publisher is None else capitalize_words(publisher),
			"views": message.views,
			"location": f"/l/{message.message_id}",
			"photo": {
				"id": message.message_id,
				"kind": "cover",
				"date": {
					"epoch": message.photo.date,
					"human": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(message.photo.date))
				},
				"file_extension": "jpeg",
				"file_id": message.photo.file_id,
				"file_name": convert_filename(book_title) + ".jpeg",
				"file_size": {
					"bytes": message.photo.file_size,
					"human": bytes_to_human(message.photo.file_size)
				},
				"file_unique_id": message.photo.file_unique_id,
				"mime_type": "image/jpeg",
				"resolution": {
					"height": message.photo.height,
					"width": message.photo.width
				},
				"downloadable": True if message.photo.file_size <= 20000000 else False,
				"location": f"/l/{message.message_id}",
				"download": f"/d/{message.message_id}" if message.photo.file_size <= 20000000 else None
			},
			"documents": [],
		}
		
		continue
		
	if message.text:
		if book:
			books.append(book)
		
		book_title = message.text.split(sep="\n")[0]
		
		author, publisher, book_type, category, narrator, duration = (
			get_author(message.text.markdown),
			get_publisher(message.text.markdown),
			get_book_type(message.text.markdown),
			get_category(message.text.markdown),
			get_narrator(message.text.markdown),
			get_duration(message.text.markdown),
		)
		
		book = {
			"id": message.message_id,
			"title": None if book_title is None else capitalize_words(book_title),
			"title_ascii_lower": None if book_title is None else capitalize_words(unidecode(book_title)).lower(),
			"type": book_type,
			"category": None if category is None else category.replace("\\", "/"),
			"duration": {
				"seconds":  human_duration_to_seconds(message.text.markdown) if book_type == "Audiobook" else None,
				"human": duration
			},
			"size": {
				"bytes": 0,
				"human": None
			},
			"author": None if author is None else capitalize_words(author),
			"narrator": None if narrator is None else capitalize_words(narrator),
			"publisher": None if publisher is None else capitalize_words(publisher),
			"views": message.views,
			"photo": None,
			"location": f"/l/{message.message_id}",
			"documents": []
		}
		
		continue
	
	if message.document:
		document = {
			"id": message.message_id,
			"kind": "audiobook" if book_type == "Audiobook" else "ebook",
			"date": {
				"epoch": message.document.date,
				"human": time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(message.document.date))
			},
			"file_extension": message.document.file_name.split(".")[-1],
			"file_id": message.document.file_id,
			"file_name": message.document.file_name.replace("_", " "),
			"file_size": {
				"bytes": message.document.file_size,
				"human": bytes_to_human(message.document.file_size)
			},
			"file_unique_id": message.document.file_unique_id,
			"mime_type": message.document.mime_type,
			"views": message.views,
			"downloadable": True if message.document.file_size <= 20000000 else False,
			"location": f"/l/{message.message_id}",
			"download": f"/d/{message.message_id}" if message.document.file_size <= 20000000 else None,
		}
		
		book["size"]["bytes"] += message.document.file_size
		book["size"]["human"] = bytes_to_human(book["size"]["bytes"])
		
		book["documents"].append(document)
	
	print(json.dumps(book, indent=4))

books.append(book)

for file in glob.glob(os.path.join(DUMPS_DIRECTORY, "/*")):
	os.remove(file)

categories, types, authors, narrators, publishers = (
	[], [], [], [], []
)

for book in books:
	category, book_type, author, narrator, publisher = (
		book.get("category"), book.get("type"), book.get("author"),
		book.get("narrator"), book.get("publisher")
	)
	
	if category is not None and category not in categories:
		categories.append(category)
	
	if book_type is not None and book_type not in types:
		types.append(book_type)
	
	if author is not None and author not in authors:
		authors.append(author)
	
	if narrator is not None and narrator not in narrators:
		narrators.append(narrator)

	if publisher is not None and publisher not in publishers:
		publishers.append(publisher)

with open(file=os.path.join(BOOKS_DIRECTORY, "categories.json"), mode="w") as file:
	file.write(json.dumps(categories))

with open(file=os.path.join(BOOKS_DIRECTORY, "types.json"), mode="w") as file:
	file.write(json.dumps(types))

with open(file=os.path.join(BOOKS_DIRECTORY, "authors.json"), mode="w") as file:
	file.write(json.dumps(authors))

with open(file=os.path.join(BOOKS_DIRECTORY, "narrators.json"), mode="w") as file:
	file.write(json.dumps(narrators))

with open(file=os.path.join(BOOKS_DIRECTORY, "publishers.json"), mode="w") as file:
	file.write(json.dumps(publishers))

with open(file=os.path.join(BOOKS_DIRECTORY, "books.json"), mode="w") as file:
	file.write(json.dumps(books))

with open(file=os.path.join(DUMPS_DIRECTORY, "books.json"), mode="w") as file:
	file.write(json.dumps(books))

pd = pandas.read_json(os.path.join(BOOKS_DIRECTORY, "books.json"))

pd.to_excel(os.path.join(DUMPS_DIRECTORY, "books.xlsx"))
pd.to_csv(os.path.join(DUMPS_DIRECTORY, "books.csv"))

with open(file=os.path.join(MESSAGES_DIRECTORY, "message_ids.json"), mode="w") as file:
	file.write(json.dumps(message_ids))

