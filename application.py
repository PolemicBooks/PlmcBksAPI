from urllib.parse import quote
import os

from flask import Flask
from flask import request, redirect, render_template

from core._clients import telegram, http
from core._types import Books, Photo, Errors
from core._files import books, errors, messages, categories, types, authors, narrators, publishers
from core._utils import convert_int


app = Flask(__name__)


@app.route("/l/<int:message_id>", methods=["GET"])
def handle_location(message_id):
	
	if message_id not in messages:
		return (dict(error=errors.error_message_not_found), 404)
	else:
		return redirect(location=os.path.join("https://t.me/PolemicBooks", str(message_id)), code=301)


@app.route("/", methods=["GET"])
def handle_index():
	return render_template('index.html')


@app.route("/d/<int:message_id>", methods=["GET"])
def handle_download(message_id):
	
	if message_id not in messages:
		return (dict(error=errors.error_message_not_found), 404)
	
	media = books.get_media(message_id)
	
	if media is None:
		return (dict(error=errors.error_media_not_found), 404)
	
	if media.file_size["bytes"] > 20000000:
		return (dict(error=errors.error_media_too_large), 400)
	
	try:
		download_url = telegram.get_file_url(media.file_id)
	except:
		return (dict(error=errors.error_download_unavailable), 503)
	
	if isinstance(media, Photo):
		headers = {
			"Content-Type": media.mime_type,
			"Content-Disposition": 'inline; filename="' + quote(media.file_name) + '"',
			"Content-Location": f"/l/{message_id}",
			"Last-Modified": media.date["human"]
		}
	else:
		headers = {
			"Content-Type": media.mime_type,
			"Content-Disposition": 'attachment; filename="' + quote(media.file_name) + '"',
			"Content-Location": f"/l/{message_id}",
			"Last-Modified": media.date["human"]
		}
	
	response = http.get(download_url)
	content = response.content
	
	return (content, 200, headers)


@app.route("/s/title", methods=["GET"])
def handle_title_search():

	query, page, max_results = (
		request.args.get("query", ""),
		request.args.get("page"),
		request.args.get("max_results")
	)
	
	max_results = convert_int(max_results, 15)
	page = convert_int(page, 0)
	
	data, status = books.search_title(query, page, max_results)
	
	return (data, 200)


@app.route("/s/author", methods=["GET"])
def handle_author_search():

	query, page, max_results = (
		request.args.get("query", ""),
		request.args.get("page"),
		request.args.get("max_results")
	)
	
	max_results = convert_int(max_results, 15)
	page = convert_int(page, 0)
	
	data, status = books.search_author(query, page, max_results)
	
	return (data, status)


@app.route("/s/publisher", methods=["GET"])
def handle_publisher_search():

	query, page, max_results = (
		request.args.get("query", ""),
		request.args.get("page"),
		request.args.get("max_results")
	)
	
	max_results = convert_int(max_results, 15)
	page = convert_int(page, 0)
	
	data, status = books.search_publisher(query, page, max_results)
	
	return (data, status)


@app.route("/s/narrator", methods=["GET"])
def handle_narrator_search():

	query, page, max_results = (
		request.args.get("query", ""),
		request.args.get("page"),
		request.args.get("max_results")
	)
	
	max_results = convert_int(max_results, 15)
	page = convert_int(page, 0)
	
	data, status = books.search_narrator(query, page, max_results)
	
	return (data, status)


@app.route("/s/type", methods=["GET"])
def handle_type_search():

	query, page, max_results = (
		request.args.get("query", ""),
		request.args.get("page"),
		request.args.get("max_results")
	)
	
	max_results = convert_int(max_results, 15)
	page = convert_int(page, 0)
	
	data, status = books.search_book_type(query, page, max_results)
	
	return (data, status)


@app.route("/s/category", methods=["GET"])
def handle_category_search():

	query, page, max_results = (
		request.args.get("query", ""),
		request.args.get("page"),
		request.args.get("max_results")
	)
	
	max_results = convert_int(max_results, 15)
	page = convert_int(page, 0)
	
	data, status = books.search_category(query, page, max_results)
	
	return (data, status)


@app.route("/g/authors", methods=["GET"])
def handle_get_authors():
	return (books.authors, 200)


@app.route("/g/publishers", methods=["GET"])
def handle_get_publishers():
	return (books.publishers, 200)


@app.route("/g/narrators", methods=["GET"])
def handle_get_narrators():
	return (books.narrators, 200)


@app.route("/g/types", methods=["GET"])
def handle_get_types():
	return (books.types, 200)


@app.route("/g/categories", methods=["GET"])
def handle_get_categories():
	return (books.categories, 200)


errors = Errors(errors)

books = Books(
	authors,
	books,
	categories,
	narrators,
	types,
	publishers,
	errors
)

app.config["JSON_SORT_KEYS"] = False

if __name__ == "__main__":
    app.run()
