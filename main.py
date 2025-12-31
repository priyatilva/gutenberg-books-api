from fastapi import FastAPI, Query
from database import SessionLocal
from sqlalchemy import text

app = FastAPI(title="Project Gutenberg Books API")


@app.get("/books")
def get_books(
    book_id: str = Query(""),
    language: str = Query(""),
    author: str = Query(""),
    title: str = Query(""),
    topic: str = Query(""),
    mime_type: str = Query(""),
    page: int = 1
):
    db = SessionLocal()
    limit = 25
    offset = (page - 1) * limit

    # convert comma-separated filters to lists
    book_ids = [int(x) for x in book_id.split(",")] if book_id else []
    languages = language.split(",") if language else []
    authors = author.split(",") if author else []
    titles = title.split(",") if title else []
    topics = topic.split(",") if topic else []
    mime_types = mime_type.split(",") if mime_type else []

    base_query = """
    FROM books_book b

    LEFT JOIN books_book_authors ba ON b.id = ba.book_id
    LEFT JOIN books_author a ON ba.author_id = a.id

    LEFT JOIN books_book_languages bl ON b.id = bl.book_id
    LEFT JOIN books_language l ON bl.language_id = l.id

    LEFT JOIN books_book_subjects bsub ON b.id = bsub.book_id
    LEFT JOIN books_subject s ON bsub.subject_id = s.id

    LEFT JOIN books_book_bookshelves bbs ON b.id = bbs.book_id
    LEFT JOIN books_bookshelf bs ON bbs.bookshelf_id = bs.id

    LEFT JOIN books_format f ON b.id = f.book_id

    WHERE b.title IS NOT NULL
    """

    params = {}

    # ---- FILTERS ----

    if book_ids:
        base_query += " AND b.id = ANY(:book_ids)"
        params["book_ids"] = book_ids

    if languages:
        base_query += """
        AND EXISTS (
            SELECT 1
            FROM books_book_languages bl2
            JOIN books_language l2 ON bl2.language_id = l2.id
            WHERE bl2.book_id = b.id
            AND l2.code = ANY(:languages)
        )
        """
        params["languages"] = languages

    if authors:
        base_query += " AND (" + " OR ".join(
            [f"a.name ILIKE :author_{i}" for i in range(len(authors))]
        ) + ")"
        for i, val in enumerate(authors):
            params[f"author_{i}"] = f"%{val}%"

    if titles:
        base_query += " AND (" + " OR ".join(
            [f"b.title ILIKE :title_{i}" for i in range(len(titles))]
        ) + ")"
        for i, val in enumerate(titles):
            params[f"title_{i}"] = f"%{val}%"

    # ? FIXED TOPIC FILTER
    if topics:
        base_query += """
        AND EXISTS (
            SELECT 1
            FROM books_book_subjects bsub2
            JOIN books_subject s2 ON bsub2.subject_id = s2.id
            WHERE bsub2.book_id = b.id
            AND (""" + " OR ".join(
                [f"s2.name ILIKE :topic_{i}" for i in range(len(topics))]
            ) + """)
        )
        OR EXISTS (
            SELECT 1
            FROM books_book_bookshelves bbs2
            JOIN books_bookshelf bs2 ON bbs2.bookshelf_id = bs2.id
            WHERE bbs2.book_id = b.id
            AND (""" + " OR ".join(
                [f"bs2.name ILIKE :topic_{i}" for i in range(len(topics))]
            ) + """)
        )
        """
        for i, val in enumerate(topics):
            params[f"topic_{i}"] = f"%{val}%"

    # ? FIXED MIME-TYPE FILTER
    if mime_types:
        base_query += """
        AND EXISTS (
            SELECT 1
            FROM books_format f2
            WHERE f2.book_id = b.id
            AND f2.mime_type = ANY(:mime_types)
        )
        """
        params["mime_types"] = mime_types

    # ---- TOTAL COUNT ----
    count_query = "SELECT COUNT(DISTINCT b.id) " + base_query
    total_books = db.execute(text(count_query), params).scalar()

    # ---- MAIN QUERY ----
    data_query = """
    SELECT
        b.id,
        b.title,
        b.download_count,

        STRING_AGG(DISTINCT a.name, ', ') AS authors,
        STRING_AGG(DISTINCT l.code, ', ') AS languages,
        STRING_AGG(DISTINCT s.name, ', ') AS subjects,
        STRING_AGG(DISTINCT bs.name, ', ') AS bookshelves,

        JSON_AGG(
            DISTINCT jsonb_build_object(
                'mime_type', f.mime_type,
                'url', f.url
            )
        ) FILTER (WHERE f.url IS NOT NULL) AS formats
    """ + base_query + """
    GROUP BY b.id
    ORDER BY b.download_count DESC NULLS LAST
    LIMIT :limit OFFSET :offset
    """

    params["limit"] = limit
    params["offset"] = offset

    result = db.execute(text(data_query), params).fetchall()

    books = []
    for row in result:
        books.append({
            "id": row.id,
            "title": row.title,
            "authors": row.authors,
            "languages": row.languages,
            "subjects": row.subjects,
            "bookshelves": row.bookshelves,
            "formats": row.formats,
            "download_count": row.download_count
        })

    return {
        "total_books": total_books,
        "page": page,
        "page_size": limit,
        "books": books
    }
