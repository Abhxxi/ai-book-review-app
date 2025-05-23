import requests
from bs4 import BeautifulSoup

def suggest_books_from_goodreads(topic):
    search_url = f"https://www.goodreads.com/search?q={topic}"
    headers = {'User-Agent': 'Mozilla/5.0'}

    try:
        response = requests.get(search_url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        book_elements = soup.select('a.bookTitle span')
        suggestions = [book.get_text(strip=True) for book in book_elements[:5]]

        return suggestions if suggestions else ["No suggestions found."]
    except Exception as e:
        return [f"Error fetching suggestions: {str(e)}"]
