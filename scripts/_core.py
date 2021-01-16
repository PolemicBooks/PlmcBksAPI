import re


def get_author(text):
	
	result = re.findall(r"\n\*\*Autor\*\*:\s__(.+)__", text)
	
	if result:
		return re.sub(r"\s+", " ", result[0]).strip()


def get_publisher(text):
	
	result = re.findall(r"\n\*\*Editora\*\*:\s__(.+)__", text)
	
	if result:
		return re.sub(r"\s+", " ", result[0]).strip()


def get_book_type(text):
	
	result = re.findall(r"\n\*\*Tipo\*\*:\s__(.+)__", text)
	
	if result:
		return re.sub(r"\s+", " ", result[0]).strip()


def get_category(text):
	
	result = re.findall(r"\n\*\*Categoria\*\*:\s__(.+)__", text)
	
	if result:
		return re.sub(r"\s+", " ", result[0]).strip()


def get_narrator(text):
	
	result = re.findall(r"\n\*\*Narrador\*\*:\s__(.+)__", text)
	
	if result:
		return re.sub(r"\s+", " ", result[0]).strip()


def get_duration(text):
	
	result = re.findall(r"\n\*\*Duração\*\*:\s__(.+)__", text)
	
	if result:
		return re.sub(r"\s+", " ", result[0]).strip()
