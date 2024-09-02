from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
import sqlite3
import time
import logging
from flask_socketio import SocketIO

# Initialize logging
logging.basicConfig(filename='extraction_errors.log', level=logging.ERROR)

# Initialize SocketIO
socketio = SocketIO()

# Initialize the database
def init_db():
    conn = sqlite3.connect('goodreads_quotes.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS books
                 (id INTEGER PRIMARY KEY, title TEXT, author TEXT, link TEXT UNIQUE)''')
    c.execute('''CREATE TABLE IF NOT EXISTS highlights
                 (id INTEGER PRIMARY KEY, book_id INTEGER, highlight TEXT,
                  FOREIGN KEY(book_id) REFERENCES books(id))''')
    conn.commit()
    conn.close()

# Save book and highlights to the database
def save_to_db(book):
    conn = sqlite3.connect('goodreads_quotes.db')
    c = conn.cursor()
    
    # Insert book if it doesn't exist
    c.execute('''INSERT OR IGNORE INTO books (title, author, link) VALUES (?, ?, ?)''',
              (book['title'], book['author'], book['link']))
    
    # Get the book ID
    c.execute('SELECT id FROM books WHERE link = ?', (book['link'],))
    book_id = c.fetchone()[0]
    
    # Insert highlights
    for highlight in book['highlights']:
        c.execute('''INSERT INTO highlights (book_id, highlight) VALUES (?, ?)''', (book_id, highlight))
    
    conn.commit()
    conn.close()

# Function to extract book links from Goodreads highlights page
def extract_book_links(url):
    print("Setting up Chrome options...")
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
    chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
    
    print("Initializing WebDriver...")
    driver = webdriver.Chrome(options=chrome_options)
    driver.get(url)
    print("Navigated to URL:", url)
    
    try:
        print("Waiting for book elements to be present...")
        WebDriverWait(driver, 20).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, 'annotatedBookItem'))
        )
        print("Book elements found.")
    except Exception as e:
        print("Error waiting for book elements:", e)
        print("Printing page source for debugging...")
        print(driver.page_source)  # Print the page source for debugging
        driver.quit()
        return []
    
    page_content = driver.page_source
    soup = BeautifulSoup(page_content, 'html.parser')
    
    book_elements = soup.find_all('div', class_='annotatedBookItem')
    books = []
    for book in book_elements:
        link = book.find('a', class_='annotatedBookItem__knhLink')['href']
        title = book.find('div', class_='annotatedBookItem__bookInfo__bookTitle').get_text(strip=True)
        author = book.find('div', class_='annotatedBookItem__bookInfo__bookAuthor').find_all('span')[-1].get_text(strip=True)
        books.append({'link': link, 'title': title, 'author': author})
    
    driver.quit()
    return books

# Function to extract highlights for a specific book with retry mechanism
def extract_highlights_for_book(book_link, retries=3):
    for attempt in range(retries):
        try:
            print("Setting up Chrome options for book link:", book_link)
            chrome_options = Options()
            chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            chrome_options.add_argument("--remote-debugging-port=9222")
            chrome_options.add_argument("--ignore-certificate-errors")  # Ignore SSL certificate errors
            chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3")
            
            print("Initializing WebDriver for book link...")
            driver = webdriver.Chrome(options=chrome_options)
            driver.get(book_link)
            print("Navigated to book link:", book_link)
            
            print("Waiting for highlight elements to be present...")
            WebDriverWait(driver, 20).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, 'noteHighlightTextContainer__highlightContainer'))
            )
            print("Highlight elements found.")
            
            page_content = driver.page_source
            soup = BeautifulSoup(page_content, 'html.parser')
            
            highlight_elements = soup.find_all('div', class_='noteHighlightTextContainer__highlightContainer')
            highlights = [highlight.find('span').get_text(strip=True) for highlight in highlight_elements]
            
            driver.quit()
            return highlights
        except Exception as e:
            print(f"Error extracting highlights for book link {book_link} (attempt {attempt + 1} of {retries}):", e)
            logging.error(f"Error extracting highlights for book link {book_link} (attempt {attempt + 1} of {retries}): {e}")
            driver.quit()
            time.sleep(5)  # Wait before retrying
    return []

# Function to extract and save highlights from all books on the Goodreads highlights page
def extract_and_save_highlights(url, reextract_books=[]):
    socketio.emit('log', {'message': "Extracting book links..."})
    books = extract_book_links(url)
    
    conn = sqlite3.connect('goodreads_quotes.db')
    c = conn.cursor()
    
    skipped_books = []
    
    for book in books:
        # Check if the book is already in the database
        c.execute('SELECT id FROM books WHERE link = ?', (book['link'],))
        book_in_db = c.fetchone()
        
        if book_in_db and book['title'] not in reextract_books:
            message = f"Skipping already extracted book: {book['title']} by {book['author']}"
            print(message)
            socketio.emit('log', {'message': message})
            skipped_books.append(f"{book['title']} by {book['author']}")
            continue
        
        message = f"Extracting highlights for book: {book['title']} by {book['author']}"
        print(message)
        socketio.emit('log', {'message': message})
        book['highlights'] = extract_highlights_for_book(book['link'])
        if book['highlights']:
            save_to_db(book)  # Save to database immediately after extracting highlights
    
    conn.close()
    
    if len(skipped_books) == len(books):
        socketio.emit('log', {'message': "No books to extract quotes."})
    
    return skipped_books

# Example usage
if __name__ == "__main__":
    init_db()
    url = "https://www.goodreads.com/notes/31551289-daniel-pereira-de-melo?ref=rnlp"
    print("Starting extraction process...")
    skipped_books = extract_and_save_highlights(url)
    print("Extraction process completed.")
    print("Skipped books:", skipped_books)