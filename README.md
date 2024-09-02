# Goodreads Quotes Extractor

This project extracts quotes and highlights from Goodreads using Selenium and BeautifulSoup, and saves them into an SQLite database. The script avoids re-extracting data from books that have already been processed, unless specified otherwise. Additionally, it provides a web interface for users to start the extraction process, check progress, and view extracted quotes.

## Features

- Extracts book links and highlights from a Goodreads highlights page.
- Saves extracted data into an SQLite database.
- Avoids re-extracting data from already processed books.
- Implements a retry mechanism for handling extraction failures.
- Logs errors to a file for debugging purposes.
- Real-time logging and progress updates via WebSocket.
- Web interface for starting extraction, checking progress, and viewing quotes.

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup4
- Flask
- Flask-SocketIO
- SQLite3
- Google Chrome
- ChromeDriver

## Installation

1. **Clone the repository:**

    ```sh
    git clone https://github.com/yourusername/goodreads-quotes-extractor.git
    cd goodreads-quotes-extractor
    ```

2. **Install the required Python packages:**

    ```sh
    pip install selenium beautifulsoup4 flask flask-socketio
    ```

3. **Download and install ChromeDriver:**

    - Download ChromeDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).
    - Make sure the ChromeDriver version matches your installed version of Google Chrome. Recent Google Chrome versions do not require Chrome driver
    - Add the ChromeDriver executable to your system's PATH or your chrome.exe depending on the versions.

## Usage

1. **Initialize the database:**

    The database will be automatically initialized when you run the script for the first time.

2. **Run the Flask application:**

    ```sh
    python app.py
    ```

    The Flask application will start, and you can access the web interface at `http://127.0.0.1:5000`.

3. **Use the web interface:**

    - Open your web browser and go to `http://127.0.0.1:5000`.
    - Enter the Goodreads link in the "Goodreads Link" field and click "Start Extraction".
    - Monitor the extraction progress and view log messages in real-time.
    - Search for books, authors, or specific quotes using the search form.
    - View quotes for specific books using the book selection form.

4. **Specify a different Goodreads highlights page:**

    Update the `url` variable in the `if __name__ == "__main__":` block of `extract_goodreads_quotes.py` to specify a different Goodreads highlights page.

5. **Re-extract highlights for specific books:**

    Pass the titles of the books you want to re-extract highlights for in the `reextract_books` list in the `extract_and_save_highlights` function.

## Example

1. **Initialize the database and start the Flask application:**

    ```sh
    python app.py
    ```

2. **Open the web interface:**

    Go to `http://127.0.0.1:5000` in your web browser.

3. **Start the extraction process:**

    Enter the Goodreads link in the "Goodreads Link" field and click "Start Extraction".

4. **Monitor progress:**

    View real-time log messages and progress updates in the "Log Messages" section.

5. **Search and view quotes:**

    Use the search form to find specific quotes, books, or authors. Use the book selection form to view quotes for specific books.
