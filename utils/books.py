import datetime

from .bytes import to_human


# Esta função é usada para gerar o texto ou legenda de um livro.
def create_caption(book):
	
	caption = ""
	
	if book.type is not None:
		caption += f"<strong>Tipo</strong>: <em>{book.type.name}</em><br>"
	if book.category is not None:
		caption += f"<strong>Categoria</strong>: <em>{book.category.name}</em><br>"
	if book.genre is not None:
		caption += f"<strong>Gênero</strong>: <em>{book.genre}</em><br>"
	if book.duration is not None:
		caption += f"<strong>Duração</strong>: <em>" + str(datetime.timedelta(seconds=book.duration)) + "</em><br>"
	if book.total_size is not None:
		caption += f"<strong>Tamanho</strong>: <em>" + to_human(book.total_size) + "</em><br>"
	if book.volumes is not None:
		caption += f"<strong>Volumes</strong>: <em>{book.volumes}</em><br>"
	if book.chapters is not None:
		caption += f"<strong>Capítulos</strong>: <em>{book.chapters}</em><br>"
	if book.year is not None:
		caption += f"<strong>Ano</strong>: <em>{book.year.name}</em><br>"
	if book.author is not None:
		caption += f"<strong>Autor</strong>: <em>{book.author.name}</em><br>"
	if book.narrator is not None:
		caption += f"<strong>Narrador</strong>: <em>{book.narrator.name}</em><br>"
	if book.publisher is not None:
		caption += f"<strong>Editora</strong>: <em>{book.publisher.name}</em><br>"
	
	return caption
