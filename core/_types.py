from unidecode import unidecode

from ._utils import pagination

class Books:
	"""Um objeto representando informações sobre vários livros."""
	def __init__(
		self,
		authors,
		books,
		categories,
		narrators,
		types,
		publishers,
		errors
	):
		categories.sort()
		authors.sort()
		narrators.sort()
		types.sort()
		publishers.sort()
		
		self.books = books
		self.categories = dict(categories=categories)
		self.types = dict(types=types)
		self.authors = dict(authors=authors)
		self.narrators = dict(narrators=narrators)
		self.publishers = dict(publishers=publishers)
		self.errors = errors
	
	def get_media(self, message_id):
		for book in self.books:
			if book["id"] == message_id:
				return Photo(book["photo"])
			else:
				for document in book["documents"]:
					if document["id"] == message_id:
						return Document(document)
	
	def handle_results(self, results, page, max_results):
		if not results:
			return (dict(error=self.errors.error_no_results_found), 404)
		
		pages = pagination(results, max_results)
		
		try:
			pages[page]
		except IndexError:
			return (dict(error=self.errors.error_list_out_of_range), 400)
		
		total_results = 0
		
		for pag in pages:
			total_results += len(pag)
		
		data = {
			"pagination": {
				"total_pages": len(pages),
				"remaining_pages": len(pages) - 1 - page,
				"previous_page": (page - 1) if (page - 1) > 0 else None,
				"current_page": page,
				"next_page":  (page + 1) if (page + 1) < len(pages) else None
			},
			"results": {
				"total_results": total_results,
				"max_results": max_results,
				"results": pages[page]
			}
		}
		
		return (data, 200)
	
	def search_title(self, query, page, max_results, exact_match):
		results = []
		
		if exact_match == "yes":
			for book in self.books:
				if query in book["title"]:
					results.append(book)
		else:
			ascii_query_lower = unidecode(query).lower()
			for book in self.books:
				if ascii_query_lower in book["title_ascii_lower"]:
					results.append(book)
			
		
		return self.handle_results(results, page, max_results)
	
	def search_author(self, query, page, max_results):
		if query not in self.authors["authors"]:
			return (dict(error=self.errors.error_author_not_found), 404)
		
		results = []
		
		for book in self.books:
			if query == book["author"]:
				results.append(book)
		
		return self.handle_results(results, page, max_results)
	
	def search_publisher(self, query, page, max_results):
		if query not in self.publishers["publishers"]:
			return (dict(error=self.errors.error_publisher_not_found), 404)
		
		results = []
		
		for book in self.books:
			if query == book["publisher"]:
				results.append(book)
		
		return self.handle_results(results, page, max_results)
	
	def search_narrator(self, query, page, max_results):
		if query not in self.narrators["narrators"]:
			return (dict(error=self.errors.error_narrator_not_found), 404)
		
		results = []
		
		for book in self.books:
			if query == book["narrator"]:
				results.append(book)
		
		return self.handle_results(results, page, max_results)
	
	def search_category(self, query, page, max_results):
		if query not in self.categories["categories"]:
			return (dict(error=self.errors.error_category_not_found), 404)
		
		results = []
		
		for book in self.books:
			if query == book["category"]:
				results.append(book)
		
		return self.handle_results(results, page, max_results)
	
	def search_book_type(self, query, page, max_results):
		if query not in self.types["types"]:
			return (dict(error=self.errors.error_type_not_found), 404)
		
		results = []
		
		for book in self.books:
			if query == book["type"]:
				results.append(book)
		
		return self.handle_results(results, page, max_results)


class Errors:
	
	def __init__(self, errors):
		self.__dict__.update(errors)


class Photo:
	
	def __init__(self, photo):
		self.__dict__.update(photo)


class Document:
	
	def __init__(self, document):
		self.__dict__.update(document)

