import datetime

from .bytes import to_human


# Esta função é usada para gerar o texto ou legenda de um livro.
def create_content(book):
	
	caption = ""
	
	if book.type is not None:
		caption += f"<strong>Kind</strong>: <em>{book.type.name}</em><br>"
	if book.genre is not None:
		caption += f"<strong>Genre</strong>: <em>{book.genre}</em><br>"
	if book.duration is not None:
		caption += f"<strong>Duration</strong>: <em>" + str(datetime.timedelta(seconds=book.duration)) + "</em><br>"
	if book.total_size is not None:
		caption += f"<strong>Size</strong>: <em>" + to_human(book.total_size) + "</em><br>"
	if book.volumes is not None:
		caption += f"<strong>Volumes</strong>: <em>{book.volumes}</em><br>"
	if book.chapters is not None:
		caption += f"<strong>Chapters</strong>: <em>{book.chapters}</em><br>"
	if book.narrator is not None:
		caption += f"<strong>Narrator</strong>: <em>{book.narrator.name}</em><br>"
	
	return caption
