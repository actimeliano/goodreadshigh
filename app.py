from flask import Flask, render_template, request, jsonify
from flask_socketio import SocketIO
import sqlite3
from extract_goodreads_quotes import init_db, extract_and_save_highlights, socketio
import threading

app = Flask(__name__)
socketio.init_app(app)
progress = "Not started"
reextract_options = ""
skipped_books = []

# Function to get database connection
def get_db_connection():
    conn = sqlite3.connect('goodreads_quotes.db')
    conn.row_factory = sqlite3.Row
    return conn

# Home route
@app.route('/')
def index():
    return render_template('index.html')

# Search route
@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('query')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    conn = get_db_connection()
    highlights = conn.execute(
        "SELECT highlights.highlight, books.title, books.author FROM highlights JOIN books ON highlights.book_id = books.id WHERE highlights.highlight LIKE ? OR books.title LIKE ? OR books.author LIKE ? LIMIT ? OFFSET ?",
        ('%' + query + '%', '%' + query + '%', '%' + query + '%', limit, offset)
    ).fetchall()
    total_count = conn.execute(
        "SELECT COUNT(*) FROM highlights JOIN books ON highlights.book_id = books.id WHERE highlights.highlight LIKE ? OR books.title LIKE ? OR books.author LIKE ?",
        ('%' + query + '%', '%' + query + '%', '%' + query + '%')
    ).fetchone()[0]
    conn.close()
    return jsonify(quotes=[dict(row) for row in highlights], total_count=total_count)

# Books route
@app.route('/books')
def books():
    conn = get_db_connection()
    books = conn.execute("SELECT id, title, author FROM books").fetchall()
    conn.close()
    return jsonify(books=[dict(row) for row in books])

# Book quotes route
@app.route('/book', methods=['GET'])
def book():
    book_id = request.args.get('book_id')
    offset = int(request.args.get('offset', 0))
    limit = int(request.args.get('limit', 10))
    conn = get_db_connection()
    highlights = conn.execute(
        "SELECT highlights.highlight, books.title, books.author FROM highlights JOIN books ON highlights.book_id = books.id WHERE books.id = ? LIMIT ? OFFSET ?",
        (book_id, limit, offset)
    ).fetchall()
    total_count = conn.execute(
        "SELECT COUNT(*) FROM highlights WHERE book_id = ?",
        (book_id,)
    ).fetchone()[0]
    conn.close()
    return jsonify(quotes=[dict(row) for row in highlights], total_count=total_count)

# Start extraction route
@app.route('/start_extraction', methods=['POST'])
def start_extraction():
    global progress, reextract_options, skipped_books
    link = request.form['link']
    progress = "Extraction started..."
    reextract_options = ""
    skipped_books = []
    
    def extraction_thread():
        global progress, reextract_options, skipped_books
        init_db()
        skipped_books = extract_and_save_highlights(link)
        progress = "Extraction completed."
        if not skipped_books:
            socketio.emit('log', {'message': "No books to extract quotes."})
        # Generate re-extraction options (this is a placeholder)
        reextract_options = "<button class='reextract' data-title='Book Title'>Re-extract Book Title</button>"
    
    thread = threading.Thread(target=extraction_thread)
    thread.start()
    
    return jsonify(message="Extraction started. Check progress...")

# Check progress route
@app.route('/check_progress', methods=['GET'])
def check_progress():
    return jsonify(progress=progress, reextractOptions=reextract_options, skippedBooks=skipped_books)

# Re-extract route
@app.route('/reextract', methods=['POST'])
def reextract():
    global progress
    title = request.form['title']
    progress = f"Re-extracting {title}..."
    # Implement re-extraction logic here
    progress = f"Re-extraction of {title} completed."
    return jsonify(message=f"Re-extraction of {title} started. Check progress...")

if __name__ == '__main__':
    socketio.run(app, debug=True)