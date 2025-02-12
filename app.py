from flask import Flask, request, jsonify
import mysql.connector

app = Flask(__name__)

# Connect to MySQL database
def get_db_connection():
    return mysql.connector.connect(
        host='sayalidolas.mysql.pythonanywhere-services.com',  # PythonAnywhere database host
        user='sayalidolas',  # Your PythonAnywhere username
        password='Sayali@2025',  # Your MySQL password (same as PythonAnywhere password)
        database='sayalidolas$gutendex'  # Database name
    )
@app.route('/search', methods=['GET'])
def search_books():
    try:
        # Get filter parameters from query string (default values for limit and offset)
        gutenberg_id = request.args.get('gutenberg_id', '')  # Filter by Gutenberg ID
        mime_type = request.args.get('mime_type', '')        # Filter by MIME type
        title = request.args.get('title', '')                # Filter by title
        author = request.args.get('author', '')              # Filter by author
        language = request.args.get('language', '')          # Filter by language
        topic = request.args.get('topic', '')                # Filter by topic (subject or bookshelf)
        limit = int(request.args.get('limit', 25))           # Default limit = 25
        offset = int(request.args.get('offset', 0))          # Default offset = 0

        # Base SQL query
        query = """
            SELECT b.title, a.name AS author, b.gutenberg_id, b.media_type,
                   l.code AS language, s.name AS subject, bshelf.name AS bookshelf,
                   f.mime_type, f.url, b.download_count
            FROM books_book b
            LEFT JOIN books_book_authors ba ON b.id = ba.book_id
            LEFT JOIN books_author a ON ba.author_id = a.id
            LEFT JOIN books_book_languages bl ON b.id = bl.book_id
            LEFT JOIN books_language l ON bl.language_id = l.id
            LEFT JOIN books_book_subjects bs ON b.id = bs.book_id
            LEFT JOIN books_subject s ON bs.subject_id = s.id
            LEFT JOIN books_book_bookshelves bks ON b.id = bks.book_id
            LEFT JOIN books_bookshelf bshelf ON bks.bookshelf_id = bshelf.id
            LEFT JOIN books_format f ON b.id = f.book_id
            WHERE 1=1
        """

        # Parameters for SQL query
        params = []

        # Adding filters dynamically using parameterized queries to prevent SQL injection
        if gutenberg_id:
            query += " AND b.gutenberg_id = %s"
            params.append(gutenberg_id)
        if mime_type:
            query += " AND f.mime_type LIKE %s"
            params.append(f"%{mime_type}%")  # Case-insensitive partial match
        if title:
            query += " AND LOWER(b.title) LIKE %s"
            params.append(f"%{title.lower()}%")
        if author:
            query += " AND LOWER(a.name) LIKE %s"
            params.append(f"%{author.lower()}%")
        if language:
            query += " AND LOWER(l.code) LIKE %s"
            params.append(f"%{language.lower()}%")
        if topic:
            query += " AND (LOWER(s.name) LIKE %s OR LOWER(bshelf.name) LIKE %s)"
            params.append(f"%{topic.lower()}%")
            params.append(f"%{topic.lower()}%")

        # Add limit and offset for pagination
        query += " LIMIT %s OFFSET %s"
        params.append(limit)
        params.append(offset)

        # Connect to the database and execute the query
        connection = get_db_connection()
        cursor = connection.cursor(dictionary=True)
        cursor.execute(query, params)
        books = cursor.fetchall()

        # Return the results as JSON
        return jsonify({'books': books, 'total': len(books)})

    except mysql.connector.Error as err:
        return jsonify({'error': f"Database error: {err}"}), 500
    except Exception as e:
        return jsonify({'error': f"Internal server error: {str(e)}"}), 500
    finally:
        if 'cursor' in locals():
            cursor.close()
        if 'connection' in locals():
            connection.close()

if __name__ == '__main__':
    app.run(debug=True)
# @app.route('/search', methods=['GET'])
# def search_books():
#     try:
#         # Get filter parameters from query string (default values for limit and offset)
#         author = request.args.get('author', '')
#         language = request.args.get('language', '')
#         topic = request.args.get('topic', '')
#         limit = int(request.args.get('limit', 25))  # Default to 25 if not provided
#         offset = int(request.args.get('offset', 0))  # Default to 0 if not provided

#         # Build the SQL query with the filters
#         query = """
#             SELECT b.title, a.name AS author, b.gutenberg_id, b.media_type, b.title,
#                   l.code AS language, s.name AS subject, bshelf.name AS bookshelf,
#                   f.mime_type, f.url, b.download_count
#             FROM books_book b
#             LEFT JOIN books_book_authors ba ON b.id = ba.book_id
#             LEFT JOIN books_author a ON ba.author_id = a.id
#             LEFT JOIN books_book_languages bl ON b.id = bl.book_id
#             LEFT JOIN books_language l ON bl.language_id = l.id
#             LEFT JOIN books_book_subjects bs ON b.id = bs.book_id
#             LEFT JOIN books_subject s ON bs.subject_id = s.id
#             LEFT JOIN books_book_bookshelves bks ON b.id = bks.book_id
#             LEFT JOIN books_bookshelf bshelf ON bks.bookshelf_id = bshelf.id
#             LEFT JOIN books_format f ON b.id = f.book_id
#             WHERE 1=1
#         """

#         # Adding filters dynamically
#         if author:
#             query += f" AND a.name LIKE '%{author}%'"
#         if language:
#             query += f" AND l.code LIKE '{language}'"
#         if topic:
#             query += f" AND (s.name LIKE '%{topic}%' OR bshelf.name LIKE '%{topic}%')"

#         # Add limit and offset for pagination
#         query += f" LIMIT {limit} OFFSET {offset}"

#         # Connect to the database and execute the query
#         connection = get_db_connection()
#         cursor = connection.cursor(dictionary=True)
#         cursor.execute(query)
#         books = cursor.fetchall()

#         # Return the results as JSON
#         return jsonify({'books': books, 'total': len(books)})

#     except mysql.connector.Error as err:
#         return jsonify({'error': f"Database error: {err}"}), 500
#     except Exception as e:
#         return jsonify({'error': f"Internal server error: {str(e)}"}), 500
#     finally:
#         cursor.close()
#         connection.close()

# if __name__ == '__main__':
#     app.run(debug=True)
