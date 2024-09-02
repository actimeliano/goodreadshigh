# Goodreads Quotes Extractor

This project extracts quotes and highlights from Goodreads using Selenium and BeautifulSoup, and saves them into an SQLite database. The script avoids re-extracting data from books that have already been processed, unless specified otherwise.

## Features

- Extracts book links and highlights from a Goodreads highlights page.
- Saves extracted data into an SQLite database.
- Avoids re-extracting data from already processed books.
- Implements a retry mechanism for handling extraction failures.
- Logs errors to a file for debugging purposes.

## Requirements

- Python 3.x
- Selenium
- BeautifulSoup4
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
    pip install selenium beautifulsoup4
    ```

3. **Download and install ChromeDriver:**

    - Download ChromeDriver from [here](https://sites.google.com/a/chromium.org/chromedriver/downloads).
    - Make sure the ChromeDriver version matches your installed version of Google Chrome. Recent Google Chrome versions do not require Chrome driver
    - Add the ChromeDriver executable to your system's PATH or your chrome.exe depending on the versions.

## Usage

1. **Initialize the database:**

    The database will be automatically initialized when you run the script for the first time.

2. **Run the script:**

    ```sh
    python extract_goodreads_quotes.py
    ```

    The script will extract book links and highlights from the specified Goodreads highlights page and save them into the SQLite database.

3. **Specify a different Goodreads highlights page:**

    Update the `url` variable in the `if __name__ == "__main__":` block to specify a different Goodreads highlights page.

4. **Re-extract highlights for specific books:**

    Pass the titles of the books you want to re-extract highlights for in the `reextract_books` list in the `extract_and_save_highlights` function.
