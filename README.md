--> Project Gutenberg Books API

A RESTful API built using FastAPI and PostgreSQL to query and access books from the Project Gutenberg repository.
The API supports multiple filters, pagination, and returns structured JSON responses.

> Features

Query books using multiple filter criteria

Supports pagination (25 books per page)

Returns books ordered by popularity (download count)

Uses PostgreSQL database dump from Project Gutenberg

Returns download links with mime-types

> Tech Stack

Backend: FastAPI

Database: PostgreSQL

Server: Uvicorn

Language: Python 

> Database Used

PostgreSQL database dump provided in the assessment

> Tables include:

books_book

books_author

books_language

books_subject

books_bookshelf

books_format

> API Endpoint
GET /books

Fetch books using zero or more filters.

> Supported Query Parameters
Parameter	                                          Description
book_id	                             Project Gutenberg book IDs (comma-separated)
language	                             Language codes (e.g. en,fr)
author	                             Author name (case-insensitive, partial match)
title	                                     Book title (case-insensitive, partial match)
topic	                                     Matches subjects OR bookshelves
mime_type	                     Filter by format (e.g. application/pdf)
page	                                     Page number (default = 1)

> Multiple values supported for each filter
> Multiple filters can be combined in a single request

> Example Requests
/books?language=en,fr&topic=child&page=1

/books?author=austen&mime_type=application/pdf

/books?book_id=1343,12

> How to Run Locally
1 Clone Repository
git clone https://github.com/priyatilva/gutenberg-books-api
cd gutenberg-books-api

2 Create Virtual Environment
python3 -m venv venv
source venv/bin/activate

3 Install Dependencies
pip install -r requirements.txt

4 Configure Database

Update DATABASE_URL in database.py:

postgresql+psycopg2://username:password@localhost:5432/gutenberg

5 Run Server
uvicorn main:app --reload


Open browser:

http://127.0.0.1:8000/books?language=en,fr&topic=child&page=1

> Repository Structure
gutenberg-api/
|-- main.py
|-- database.py
|-- requirements.txt
|-- README.md
|-- .gitignore

> Assessment Requirements Status

1 Used provided database dump
2 Implemented REST API
3 All required filters supported
4 Pagination implemented
5 JSON response format
6 Publicly accessible API
7 Code hosted on GitHub

> Author

Priya Tilva
MCA Student | Backend Development | FastAPI | PostgreSQL