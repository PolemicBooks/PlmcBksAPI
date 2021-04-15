#!/usr/bin/python3

# -*- coding: utf-8 -*-

# Built-in packages
import argparse
from typing import Optional
import html
import time
import urllib.parse
import os
import sys
import re

# Third-party packages
import httpx
from fastapi import (
	FastAPI,
	Header,
	Path,
	Query,
	Request,
	Response,
	status
)
from fastapi.responses import (
	ORJSONResponse,
	StreamingResponse,
	RedirectResponse
)
from plmcbks.config.files import LAST_MODIFIED
from pyrogram.errors import FloodWait
import plmcbks
import pyrogram
import uvicorn

# Configuration
from config.feeds import rss, opds
from config.limits import limits
from config.metadata import openapi
from config.pyrogram import config
from config.urls import urls
from config.resolvers import resolvers
from config.headers import headers

# Utils
from utils.streaming import stream_from_url
from utils.books import create_caption
from utils.opds import create_content
from utils.paginations import create_pagination

app = FastAPI(
	title="PlmcBksAPI",
	description="Interaja com o acervo de livros, audiolivros, comics e mangás.",
	version="0.1",
	openapi_url="/openapi.json",
	openapi_tags=openapi.TAGS,
	docs_url="/",
	redoc_url=None,
	default_response_class=ORJSONResponse
)

books_list = list(plmcbks.books)
categories_list = list(plmcbks.categories)
authors_list = list(plmcbks.authors)
artists_list = list(plmcbks.artists)
narrators_list = list(plmcbks.narrators)
publishers_list = list(plmcbks.publishers)
types_list = list(plmcbks.types)
years_list = list(plmcbks.years)
covers_list = list(plmcbks.covers)
documents_list = list(plmcbks.documents)

pclient = None
httpclient = None

rate_limit = None
last_modified = time.strftime(
	"%a, %d %b %Y %H:%M:%S GMT", time.localtime(LAST_MODIFIED))

clients_ok = False

# https://stackoverflow.com/a/8391735
sys.stdout = open(file=os.devnull, mode="w")

@app.get("/books", tags=["interações"])
def get_books(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros disponíveis.
	"""
	
	objects_pagination = create_pagination(books_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/books/{book_id}", tags=["interações"])
def get_book_by_id(
	book_id: int = Path(..., title="Identificação numérica do livro", description="Identificação do livro.", ge=limits.MIN_ID, le=limits.MAX_ID)
):
	"""
	Este método retornará informações sobre um livro em específico.
	"""
	
	book = plmcbks.books.get(book_id)
	
	if book is None:
		content = {"error": "book not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	return dict(book)


@app.get("/categories", tags=["interações"])
def get_categories(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todas as categorias disponíveis.
	"""
	
	objects_pagination = create_pagination(categories_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/categories/{category_id}", tags=["interações"])
def get_books_by_category(
	category_id: int = Path(..., title="Identificação numérica da categoria", description="Identificação da categoria.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará todos os livros presentes na categoria em questão.
	"""
	
	category = plmcbks.categories.get(category_id)
	
	if category is None:
		content = {"error": "category not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = category.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/authors", tags=["interações"])
def get_authors(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os autores disponíveis.
	"""
	
	objects_pagination = create_pagination(authors_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/authors/{author_id}", tags=["interações"])
def get_books_by_author(
	author_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros escritos pelo autor em questão.
	"""
	
	author = plmcbks.authors.get(author_id)
	
	if author is None:
		content = {"error": "author not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = author.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/artists", tags=["interações"])
def get_artists(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os artistas disponíveis.
	"""
	
	objects_pagination = create_pagination(artists_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/artists/{artist_id}", tags=["interações"])
def get_books_by_artist(
	artist_id: int = Path(..., title="Identificação numérica do artista", description="Identificação do artista.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros ilustrados pelo artista em questão.
	"""
	
	artist = plmcbks.artists.get(artist_id)
	
	if artist is None:
		content = {"error": "artist not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = artist.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/narrators", tags=["interações"])
def get_narrators(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os narradores disponíveis
	"""
	
	objects_pagination = create_pagination(narrators_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/narrators/{narrator_id}", tags=["interações"])
def get_books_by_narrator(
	narrator_id: int = Path(..., title="Identificação numérica do narrador", description="Identificação da narrador.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros narrados pelo narrador em questão.
	"""
	
	narrator = plmcbks.narrators.get(narrator_id)
	
	if narrator is None:
		content = {"error": "narrator not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = narrator.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/publishers", tags=["interações"])
def get_publishers(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todas as editoras disponíveis.
	"""
	
	objects_pagination = create_pagination(publishers_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/publishers/{publisher_id}", tags=["interações"])
def get_books_by_publisher(
	publisher_id: int = Path(..., title="Identificação numérica da editora", description="Identificação da editora.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros publicados pela editora em questão.
	"""
	
	publisher = plmcbks.publishers.get(publisher_id)
	
	if publisher is None:
		content = {"error": "publisher not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = publisher.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/types", tags=["interações"])
def get_types(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os tipos disponíveis.
	"""
	
	objects_pagination = create_pagination(types_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/types/{type_id}", tags=["interações"])
def get_books_by_type(
	type_id: int = Path(..., title="Identificação numérica do tipo", description="Identificação do tipo.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros do tipo em questão.
	"""
	
	type = plmcbks.types.get(type_id)
	
	if type is None:
		content = {"error": "type not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = type.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/years", tags=["interações"])
def get_years(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os anos de publicação disponíveis.
	"""
	
	objects_pagination = create_pagination(years_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/years/{year_id}", tags=["interações"])
def get_books_by_year(
	year_id: int = Path(..., title="Identificação numérica do ano", description="Identificação do ano.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros publicados no ano em questão.
	"""
	
	year = plmcbks.years.get(year_id)
	
	if year is None:
		content = {"error": "year not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = year.get_books(plmcbks.books)
	objects_pagination = create_pagination(list(books), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/books", tags=["buscas"])
def search_books(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por livros.
	"""
	
	if search_type == "fast":
		results = plmcbks.books.fast_search(query_name)
	else:
		results = plmcbks.books.slow_search(query_name)
	
	if not results:
		content = {"error": "no books found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/authors", tags=["buscas"])
def search_authors(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por autores.
	"""
	
	if search_type == "fast":
		results = plmcbks.authors.fast_search(query_name)
	else:
		results = plmcbks.authors.slow_search(query_name)
	
	if not results:
		content = {"error": "no authors found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/artists", tags=["buscas"])
def search_artists(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por artistas.
	"""
	
	if search_type == "fast":
		results = plmcbks.artists.fast_search(query_name)
	else:
		results = plmcbks.artists.slow_search(query_name)
	
	if not results:
		content = {"error": "no artists found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/narrators", tags=["buscas"])
def search_narrators(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por narradores.
	"""
	
	if search_type == "fast":
		results = plmcbks.narrators.fast_search(query_name)
	else:
		results = plmcbks.narrators.slow_search(query_name)
	
	if not results:
		content = {"error": "no narrators found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/publishers", tags=["buscas"])
def search_publishers(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por editoras.
	"""
	
	if search_type == "fast":
		results = plmcbks.publishers.fast_search(query_name)
	else:
		results = plmcbks.publishers.slow_search(query_name)
	
	if not results:
		content = {"error": "no publishers found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/categories", tags=["buscas"])
def search_categories(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por categorias.
	"""
	
	if search_type == "fast":
		results = plmcbks.categories.fast_search(query_name)
	else:
		results = plmcbks.categories.slow_search(query_name)
	
	if not results:
		content = {"error": "no categories found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/types", tags=["buscas"])
def search_types(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por tipos.
	"""
	
	if search_type == "fast":
		results = plmcbks.types.fast_search(query_name)
	else:
		results = plmcbks.types.slow_search(query_name)
	
	if not results:
		content = {"error": "no types found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/search/years", tags=["buscas"])
def search_years(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por anos.
	"""
	
	if search_type == "fast":
		results = plmcbks.years.fast_search(query_name)
	else:
		results = plmcbks.years.slow_search(query_name)
	
	if not results:
		content = {"error": "no years found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(list(results), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/documents", tags=["mídias"])
def get_documents(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os documentos disponíveis.
	"""
	
	objects_pagination = create_pagination(documents_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/documents/{document_id}", tags=["mídias"])
def get_document_by_id(
	document_id: int = Path(..., title="Identificação numérica dd documento", description="Identificação do documento.", ge=limits.MIN_ID, le=limits.MAX_ID)
):
	"""
	Este método retornará informações sobre o documento em questão.
	"""
	
	document = plmcbks.documents.get(document_id)
	
	if document is None:
		content = {"error": "document not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	return dict(document)


@app.get("/download/{document_id}", tags=["mídias"])
async def download_document_by_id(
	document_id: int = Path(..., title="Identificação numérica dd documento", description="Identificação do documento.", ge=limits.MIN_ID, le=limits.MAX_ID)
):
	"""
	Use este método para baixar o documento em questão.
	"""
	
	global rate_limit
	
	if not clients_ok:
		await build_clients()
	
	if rate_limit:
		remaining_seconds = int(time.time()) - rate_limit
		if remaining_seconds > 0:
			content = {"error": f"too many requests, retry after {remaining_seconds} seconds"}
			headers = {"Retry-After": str(remaining_seconds)}
			status_code = status.HTTP_503_SERVICE_UNAVAILABLE
			return ORJSONResponse(
				content=content, status_code=status_code, headers=headers)
		else:
			rate_limit = None
	
	document = plmcbks.documents.get(document_id)
	book = document.get_book(plmcbks.books)
	
	if document is None:
		content = {"error": "document not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	headers = {
		"Last-Modified": time.strftime(
			"%a, %d %b %Y %H:%M:%S GMT", time.localtime(document.date)),
		"Content-Type": document.mime_type,
		"Content-Length": str(document.file_size),
		"Content-Disposition": 'attachment; filename="{}"'.format(
			urllib.parse.quote(f"{book.title}.{document.file_extension}" if book.title is not None else f"cover.{cover.file_extension}")),
	}
	
	if document.file_gdrive_id is not None:
		async with httpclient.get(f"https://drive.google.com/uc?id={document.file_gdrive_id}") as response:
			url = str(response.url)
		
		if re.match(r"^https://doc-[0-9a-z]+-[0-9a-z]+-docs\.googleusercontent\.com/.+", url):
			if response.status == 200:
				headers["Content-Location"] = url
				content_streaming = stream_from_url(httpclient, url)
				return StreamingResponse(content_streaming, headers=headers)
				
			status_code = status.HTTP_302_FOUND
			return RedirectResponse(url=url, status_code=status_code)
	
	try:
		message = await pclient.get_messages(
			chat_id=-1001436494509, message_ids=document.message_id)
	except FloodWait as e:
		rate_limit = int(time.time()) + e.x
		
		content = {"error": "we don't have enough resources to serve this file at this moment"}
		headers = {"Retry-After": str(e.x)}
		status_code = status.HTTP_503_SERVICE_UNAVAILABLE
		return ORJSONResponse(
			content=content, status_code=status_code, headers=headers)
	else:
		content = await pclient.stream_media(message)
	
	return StreamingResponse(content=content, headers=headers)


@app.get("/covers", tags=["mídias"])
def get_covers(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todas as imagens de capa disponíveis.
	"""
	
	objects_pagination = create_pagination(covers_list, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	data = {
		"pagination": {
			"total_pages": len(objects_pagination),
			"remaining_pages": len(objects_pagination) - 1 - page_number,
			"previous_page": (page_number - 1) if (page_number - 1) > -1 else None,
			"current_page": page_number,
			"next_page":  (page_number + 1) if (page_number + 1) < len(objects_pagination) else None
		},
		"results": {
			"total_results": sum(len(page) for page in objects_pagination),
			"max_results": max_items,
			"display_results": len(objects),
			"items": objects
		}
	}
	
	return data


@app.get("/covers/{cover_id}", tags=["mídias"])
def get_cover_by_id(
	cover_id: int = Path(..., title="Identificação numérica da capa", description="Identificação da capa.", ge=limits.MIN_ID, le=limits.MAX_ID)
):
	"""
	Este método retornará informações sobre a imagem de capa em questão.
	"""
	
	cover = plmcbks.covers.get(cover_id)
	
	if cover is None:
		content = {"error": "cover not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	return dict(cover)


@app.get("/view/{cover_id}", tags=["mídias"])
async def view_cover_by_id(
	cover_id: int = Path(..., title="Identificação numérica da capa", description="Identificação da capa.", ge=limits.MIN_ID, le=limits.MAX_ID)
):
	"""
	Use este método para visualizar a imagem de capa em questão.
	"""
	
	global rate_limit
	
	if not clients_ok:
		await build_clients()
	
	if rate_limit:
		remaining_seconds = int(time.time()) - rate_limit
		if remaining_seconds > 0:
			content = {"error": f"too many requests, retry after {remaining_seconds} seconds"}
			headers = {"Retry-After": str(remaining_seconds)}
			status_code = status.HTTP_503_SERVICE_UNAVAILABLE
			return ORJSONResponse(
				content=content, status_code=status_code, headers=headers)
		else:
			rate_limit = None
	
	cover = plmcbks.covers.get(cover_id)
	book = cover.get_book(plmcbks.books)
	
	if cover is None:
		content = {"error": "cover not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	headers = {
		"Last-Modified": time.strftime(
			"%a, %d %b %Y %H:%M:%S GMT", time.localtime(cover.date)),
		"Content-Type": cover.mime_type,
		"Content-Length": str(cover.file_size),
		"Content-Disposition": 'inline; filename="{}"'.format(
			urllib.parse.quote(f"{book.title}.{cover.file_extension}" if book.title is not None else f"cover.{cover.file_extension}")),
	}
	
	if cover.file_gdrive_id is not None:
		async with httpclient.stream('GET', f"https://drive.google.com/uc?id={cover.file_gdrive_id}") as response:
			url = str(response.url)
		
		if re.match(r"^https://doc-[0-9a-z]+-[0-9a-z]+-docs\.googleusercontent\.com/.+", url):
			if response.status_code == 200:
				headers["Content-Location"] = url
				content_streaming = stream_from_url(httpclient, url)
				return StreamingResponse(content_streaming, headers=headers)
				
			status_code = status.HTTP_302_FOUND
			return RedirectResponse(url=url, status_code=status_code)
	
	try:
		message = await pclient.get_messages(
			chat_id=-1001436494509, message_ids=cover.message_id)
	except FloodWait as e:
		rate_limit = int(time.time()) + e.x
		
		content = {"error": "we don't have enough resources to serve this file at this moment"}
		headers = {"Retry-After": str(e.x)}
		status_code = status.HTTP_503_SERVICE_UNAVAILABLE
		return ORJSONResponse(
			content=content, status_code=status_code, headers=headers)
	else:
		content = await pclient.stream_media(message)
	
	return StreamingResponse(content=content, headers=headers)


@app.get("/rss", tags=["rss"])
def rss_feed(
	max_items: Optional[int] = Query(50, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará um feed RSS contendo os livros adicionados recentemente.
	"""
	
	books = plmcbks.books.list()[-max_items:]
	books.reverse()
	
	items = (
		rss.ITEM_BASE.format(
			html.escape(book.title),
			urls.PRIVATE_CHAT_URL + '/' + str(book.message_id),
			urls.PRIVATE_CHAT_URL + '/' + str(book.message_id),
			urls.API_URL + "/download/" + str(book.documents[0].message_id), book.documents[0].file_size, book.documents[0].mime_type,
			html.escape("plmcbks@pm.me (Polemic Books)"),
			time.strftime("%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date)),
			html.escape(
				"<p>"
				+ f'<img src="{urls.API_URL + "/view/" + str(book.cover.id)}" width="{book.cover.resolution.width}" height="{book.cover.resolution.height}" referrerpolicy="no-referrer">'
				+ create_caption(book)
				+ f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>'
				"</p>"
			)
		) for book in books
	)
	
	content = rss.BASE.format("".join(items))
	
	return Response(content=content, media_type="application/rss+xml")


@app.get("/opds", tags=["opds"])
def opds_home():
	"""
	Este método retornará uma listagem com opções disponíveis para navegação.
	"""
	
	entries = [
		("Autores", "autores", "https://polemicbooks.github.io/images/authors.jpg", last_modified, "/opds/authors", "Listagem de autores"),
		("Artistas", "artistas", "https://polemicbooks.github.io/images/artists.jpg", last_modified, "/opds/artists", "Listagem de artistas"),
		("Narradores", "narradores", "https://polemicbooks.github.io/images/narrators.jpg", last_modified, "/opds/narrators", "Listagem de narradores"),
		("Editoras", "editoras", "https://polemicbooks.github.io/images/publishers.jpg", last_modified, "/opds/publishers", "Listagem de editoras"),
		("Categorias", "categorias", "https://polemicbooks.github.io/images/categories.jpg", last_modified, "/opds/categories", "Listagem de categorias"),
		("Tipos", "tipos", "https://polemicbooks.github.io/images/types.jpg", last_modified, "/opds/types", "Listagem de tipos"),
		("Anos", "anos", "https://polemicbooks.github.io/images/years.jpg", last_modified, "/opds/years", "Listagem de anos"),
		("Recentes", "recentes", "https://polemicbooks.github.io/images/books.jpg", last_modified, "/opds/recent-books", "Livros recentes"),
		("Antigos", "antigos", "https://polemicbooks.github.io/images/books.jpg", last_modified, "/opds/old-books", "Livros antigos")
	]
	
	items = [
		opds.ITEM_BASE.format(
			title,
			single_id,
			image,
			last_update,
			endpoint,
			text
		) for (
			title, single_id, image, last_update, endpoint, text
		) in entries
	]
	
	content = opds.BASE.format(
		"Polemic Books",
		last_modified,
		"https://polemicbooks.github.io/images/polemicbooks.jpg",
		"Pesquise ou baixe ebooks, audiobooks, comics e mangás."
	) + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/authors", tags=["opds"])
def opds_get_authors(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os autores disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.authors.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(entity.name),
			f"author:{entity.id}",
			"https://polemicbooks.github.io/images/authors.jpg",
			last_modified,
			f"/opds/authors/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Autores ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/authors.jpg",
		"Confira abaixo a lista de autores"
	) + opds.SELF_BASE.format(
			f"authors?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/authors?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/authors/{author_id}", tags=["opds"])
def opds_get_books_by_author(
	author_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros escritos pelo autor em questão.
	"""
	
	author = plmcbks.authors.get(author_id)
	
	if author is None:
		content = {"error": "author not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = author.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros de {author.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/authors.jpg",
		html.escape(f"Livros escritos por {author.name}")
	) + opds.SELF_BASE.format(
			f"/opds/authors/{author_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			"/opds/authors/{author_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/artists", tags=["opds"])
def opds_get_artists(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os artistas disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.artists.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(entity.name),
			f"artist:{entity.id}",
			"https://polemicbooks.github.io/images/artists.jpg",
			last_modified,
			f"/opds/artists/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Artistas ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/artists.jpg",
		"Confira abaixo a lista de artistas"
	) + opds.SELF_BASE.format(
			f"artists?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/artists?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/artists/{artist_id}", tags=["opds"])
def opds_get_books_by_artist(
	artist_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros ilustrados pelo artista em questão.
	"""
	
	artist = plmcbks.artists.get(artist_id)
	
	if artist is None:
		content = {"error": "artist not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = artist.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros de {artist.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/artists.jpg",
		html.escape(f"Livros ilustrados por {artist.name}")
	) + opds.SELF_BASE.format(
			f"/opds/artists/{artist_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/artists/{artist_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/narrators", tags=["opds"])
def opds_get_narrators(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os narradores disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.narrators.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(entity.name),
			f"narrator:{entity.id}",
			"https://polemicbooks.github.io/images/narrators.jpg",
			last_modified,
			f"/opds/narrators/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Narradores ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/narrators.jpg",
		"Confira abaixo a lista de narradores"
	) + opds.SELF_BASE.format(
			f"narrators?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/narrators?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/narrators/{narrator_id}", tags=["opds"])
def opds_get_books_by_narrator(
	narrator_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros narrados pelo narrador em questão.
	"""
	
	narrator = plmcbks.narrators.get(narrator_id)
	
	if narrator is None:
		content = {"error": "narrator not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = narrator.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros de {narrator.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/narrators.jpg",
		html.escape(f"Livros narrados por {narrator.name}")
	) + opds.SELF_BASE.format(
			f"/opds/narrators/{narrator_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/narrators/{narrator_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/publishers", tags=["opds"])
def opds_get_publishers(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todas as editoras disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.publishers.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(entity.name),
			f"publisher:{entity.id}",
			"https://polemicbooks.github.io/images/publishers.jpg",
			last_modified,
			f"/opds/publishers/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Editoras ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/publishers.jpg",
		"Confira abaixo a lista de editoras"
	) + opds.SELF_BASE.format(
			f"/opds/publishers?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/publishers?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/publishers/{publisher_id}", tags=["opds"])
def opds_get_books_by_publisher(
	publisher_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros publicados pela editora editora em questão.
	"""
	
	publisher = plmcbks.publishers.get(publisher_id)
	
	if publisher is None:
		content = {"error": "publisher not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = publisher.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros de {publisher.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/publishers.jpg",
		html.escape(f"Livros publicados por {publisher.name}")
	) + opds.SELF_BASE.format(
			f"/opds/publishers/{publisher_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/publishers/{publisher_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/categories", tags=["opds"])
def opds_get_categories(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todas as categorias disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.categories.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(entity.name),
			f"category:{entity.id}",
			"https://polemicbooks.github.io/images/categories.jpg",
			last_modified,
			f"/opds/categories/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Categorias ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/categories.jpg",
		"Confira abaixo a lista de categorias"
	) + opds.SELF_BASE.format(
			f"/opds/categories?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/categories?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/categories/{category_id}", tags=["opds"])
def opds_get_books_by_category(
	category_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros presentes na categoria em questão.
	"""
	
	category = plmcbks.categories.get(category_id)
	
	if category is None:
		content = {"error": "category not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = category.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros em {category.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/categories.jpg",
		html.escape(f"Livros na categoria {category.name}")
	) + opds.SELF_BASE.format(
			f"/opds/categories/{category_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/categories/{category_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/types", tags=["opds"])
def opds_get_types(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os tipos disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.types.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(entity.name),
			f"type:{entity.id}",
			"https://polemicbooks.github.io/images/types.jpg",
			last_modified,
			f"/opds/types/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Tipos ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/types.jpg",
		"Confira abaixo a lista de tipos"
	) + opds.SELF_BASE.format(
			f"/opds/types?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/types?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/types/{type_id}", tags=["opds"])
def opds_get_books_by_type(
	type_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros do tipo em questão.
	"""
	
	type = plmcbks.types.get(type_id)
	
	if type is None:
		content = {"error": "type not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = type.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros do tipo {type.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/types.jpg",
		html.escape(f"Livros do tipo {type.name}")
	) + opds.SELF_BASE.format(
			f"/opds/types/{type_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/types/{type_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/years", tags=["opds"])
def opds_get_years(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade máxima de itens", description="Quantidade máxima de itens", ge=limits.MIN_FEED_ITEMS, le=limits.MAX_FEED_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os anos disponíveis.
	"""
	
	objects_pagination = create_pagination(plmcbks.years.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = [
		opds.ITEM_BASE.format(
			html.escape(str(entity.name)),
			f"year:{entity.id}",
			"https://polemicbooks.github.io/images/years.jpg",
			last_modified,
			f"/opds/years/{entity.id}",
			html.escape(f"Possui {entity.total_books} livro(s)")
		) for entity in objects
	]
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		f"Listagem de Anos ({page_number}/{total_pages})",
		last_modified,
		"https://polemicbooks.github.io/images/years.jpg",
		"Confira abaixo a lista de anos"
	) + opds.SELF_BASE.format(
			f"years?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/years?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/years/{year_id}", tags=["opds"])
def opds_get_books_by_year(
	year_id: int = Path(..., title="Identificação numérica do autor", description="Identificação do autor.", ge=limits.MIN_ID, le=limits.MAX_ID),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Este método retornará uma lista contendo todos os livros publicados no ano em questão.
	"""
	
	year = plmcbks.years.get(year_id)
	
	if year is None:
		content = {"error": "year not found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	books = year.get_books(plmcbks.books)
	objects_pagination = create_pagination(books.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros do tipo {year.name} ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/years.jpg",
		html.escape(f"Livros do tipo {year.name}")
	) + opds.SELF_BASE.format(
			f"/opds/years/{year_id}?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/years/{year_id}?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/search/books", tags=["opds"])
def opds_search_books(
	query_name: str = Query(..., title="Termo a ser pesquisado", description="Termo a ser pesquisado", min_length=limits.MIN_QUERY_LENGTH, max_length=limits.MAX_QUERY_LENGTH),
	search_type: Optional[str] = Query("fast", title="Tipo de pesquisa", description="Tipo de pesquisa", regex="^(?:fast|slow)$"),
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para pesquisar por livros.
	"""
	
	if search_type == "fast":
		results = plmcbks.books.fast_search(query_name)
	else:
		results = plmcbks.books.slow_search(query_name)
	
	if not results:
		content = {"error": "no books found"}
		status_code = status.HTTP_404_NOT_FOUND
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects_pagination = create_pagination(results.list(), max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Resultados da Pesquisa ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/search.jpg",
		html.escape("Resultados")
	) + opds.SELF_BASE.format(
			html.escape(f"/opds/search/books?query_name={query_name}&page_number={page_number}")
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			html.escape(f"/opds/search/books?query_name={query_name}&page_number={next_page}")
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/recent-books", tags=["opds"])
def opds_recent_books(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(100, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para obter is livros publicados recentemente.
	"""
	
	books = plmcbks.books.list()
	books.reverse()
	
	objects_pagination = create_pagination(books, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros adicionados recentemente ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/books.jpg",
		html.escape(f"Livros recentes")
	) + opds.SELF_BASE.format(
			f"/opds/recent-books?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/recent-books?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


@app.get("/opds/old-books", tags=["opds"])
def opds_old_books(
	page_number: Optional[int] = Query(0, title="Posição da página", description="Posição da página", ge=limits.MIN_PAGE_NUMBER, le=limits.MAX_PAGE_NUMBER),
	max_items: Optional[int] = Query(10, title="Quantidade de itens", description="Quantidade máxima de itens", ge=limits.MIN_PAGE_ITEMS, le=limits.MAX_PAGE_ITEMS)
):
	"""
	Use este método para obter os livros antigos.
	"""
	
	books = plmcbks.books.list()
	
	objects_pagination = create_pagination(books, max_items)
	
	if page_number > len(objects_pagination):
		content = {"error": "page_number value is out of range"}
		status_code = status.HTTP_400_BAD_REQUEST
		return ORJSONResponse(content=content, status_code=status_code)
	
	objects = objects_pagination[page_number]
	
	items = []
	
	for book in objects:
		item = ""
		item += f"<entry>\n  <title>{html.escape(book.title) if book.title is not None else 'Unknown'}</title>"
		item += f"\n  <id>book:{book.id}</id>"
		item += "\n  <updated>{}</updated>".format(
			time.strftime(
				"%a, %d %b %Y %H:%M:%S GMT", time.localtime(book.date))
		)
		item += f'\n  <link rel="http://opds-spec.org/image"\n		href="/view/{book.cover.id}"\n		type="{book.cover.mime_type}"/>'
		item += f'\n  <link rel="http://opds-spec.org/acquisition"\n		href="/download/{book.documents[0].id}"\n		type="{book.documents[0].mime_type}"/>'
		if book.author is not None:
			item += f"\n  <author>\n	<name>{html.escape(book.author.name)}</name>\n	<uri>/opds/authors/{book.author.id}?page_number={page_number}</uri>\n  </author>"
		item += "\n  <dc:language>pt</dc:language>"
		if book.publisher is not None:
			item += f"\n  <dc:publisher>{html.escape(book.publisher.name)}</dc:publisher>"
		if book.year is not None:
			item += f"\n  <dc:issued>{book.year.name}</dc:issued>"
		if book.category is not None:
			item += f'\n  <category scheme="http://www.bisg.org/standards/bisac_subject/index.html"\n		term="{book.category.id}"\n		label="{html.escape(book.category.name)}"/>'
		if book.type is not None:
			item += f"\n  <summary>{book.type.name}</summary>"
		item += f'<content type="xhtml">{html.escape(create_content(book))}'
		item += html.escape(f'<strong>Download</strong>: <em><a href="{urls.API_URL + "/download/" + str(book.documents[0].id)}">{book.title + "." + book.documents[0].file_extension if book.title is not None else "document." + book.documents[0].file_extension}</a></em>')
		item += "</content>\n</entry>"
		items.append(item)
	
	total_pages = len(objects_pagination) - 1 - page_number
	
	base_feed = opds.BASE.format(
		html.escape(f"Livros antigos ({page_number}/{total_pages})"),
		last_modified,
		"https://polemicbooks.github.io/images/books.jpg",
		html.escape(f"Livros antigos")
	) + opds.SELF_BASE.format(
			f"/opds/old-books?page_number={page_number}"
		)
	
	next_page = page_number + 1
	
	if next_page < total_pages:
		base_feed += opds.NEXT_PAGE_BASE.format(
			f"/opds/old-books?page_number={next_page}"
		)
	
	content = base_feed + "".join(items) + "</feed>"
	
	return Response(content=content, media_type="application/atom+xml")


async def build_clients() -> None:
	"""
	Este método cria os clientes do Pyrogram (para acesso a API do Telegram) e
	AioHTTP (para requisições HTTP em geral).
	"""
	
	global pclient # Pyrogram client
	global httpclient # AioHTTP client
	
	global clients_ok
	
	# Pyrogram client
	pclient = pyrogram.Client(**config.PYROGRAM_OPTIONS)
	await pclient.start()
	
	httpclient = httpx.AsyncClient(http2=True)
	
	clients_ok = True
	
if __name__ == "__main__":
	
	parser = argparse.ArgumentParser()
	
	parser.add_argument("--host", default="127.0.0.1")
	parser.add_argument("--port", type=int, default=8080)
	
	options = parser.parse_args()
	
	uvicorn.run(
		app=app,
		host=options.host,
		port=options.port,
		access_log=False,
		log_level="error",
		headers=headers.HTTP_HEADERS
	)

	