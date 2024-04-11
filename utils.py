import os
import urllib
from bs4 import BeautifulSoup
import pickle
import requests

def fetch_page(url, cache_dir="cache"):
    """Fetches the content of a web page, using caching for efficiency.

    This function retrieves the HTML content of a given URL. It first checks
    if the content is already cached in a local file. If it is, the cached
    content is loaded and returned. Otherwise, the function fetches the content
    from the web using a user-agent header and stores it in the cache directory
    before returning it.

    Args:
        url (str): The URL of the web page to fetch.
        cache_dir (str, optional): The directory to store cached web pages.
            Defaults to "cache".

    Returns:
        BeautifulSoup: The parsed HTML content of the web page.
    """

    cache_file = os.path.join(cache_dir, f"{url.replace('/', '_')}.pkl")
    if os.path.exists(cache_file):
        with open(cache_file, 'rb') as f:
            return pickle.load(f)
    else:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=300) as response:
            soup = BeautifulSoup(response, 'lxml')  # Using lxml parser
            os.makedirs(cache_dir, exist_ok=True)
            with open(cache_file, 'wb') as f:
                pickle.dump(soup, f)
            return soup
        
def get_movie_details(url):
    """
    Scrapes movie details from the provided IMDb URL.

    Args:
        url (str): The URL of the IMDb movie page.

    Returns:
        dict: A dictionary containing the following movie details:
            - Title: The title of the movie.
            - Year: The release year of the movie.
            - Genre: The genre(s) of the movie.
            - Rating: The IMDb rating of the movie.
            - Runtime: The runtime of the movie in minutes.
            - Certificate: The certificate/rating of the movie.
            - Directors: A list of the movie's directors.
            - Cast: A list of the movie's cast members.
            - Description: The description of the movie.
    """
    movie_details = {}

    response = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'})
    if response.status_code != 200:
        print("Failed to retrieve movie details:", response.status_code)
        return movie_details

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract title, year, genre, and rating
    title = soup.title.text.split('- IMDb')[0]
    year = None
    year_tag = soup.find(lambda tag: tag.name == 'a' and 'releaseinfo' in tag.get('href', ''))
    if year_tag:
        year_text = year_tag.text.strip()
        if year_text.isdigit():
            year = int(year_text)
    genre = ', '.join([span.text.strip() for span in soup.find_all('a', class_="ipc-chip ipc-chip--on-baseAlt")])
    rating = float(soup.find('span', class_='sc-bde20123-1 cMEQkK').text)

    # Extract runtime and certificate
    meta_tag = soup.find('meta', property='og:description')
    if meta_tag:
        content = meta_tag.get('content')
        runtime = None
        certificate = None
        if content:
            parts = content.split('|')
            if len(parts) == 2:
                runtime_str, certificate = parts
                runtime_str = runtime_str.strip()
                if runtime_str:
                    time_parts = runtime_str.split()
                    if len(time_parts) == 2:
                        hours, minutes = time_parts
                        runtime = int(hours[:-1]) * 60 + int(minutes[:-1])
                certificate = certificate.strip()

    # Extract full credits URL segment
    credits_url_segment = None
    try:
        credits_url_segment = soup.find(lambda tag: tag.name == 'a' and 'fullcredits' in tag.get('href', '')).get('href')
    except AttributeError:
        print("Failed to find full credits URL segment")
        return movie_details
    
    # Fetch full credits page
    base_url = "https://www.imdb.com"
    credits_response = requests.get(f'{base_url}{credits_url_segment}', timeout= 600)
    if credits_response.status_code != 200:
        print("Failed to retrieve full credits page:", credits_response.status_code)
        return movie_details

    credits_soup = BeautifulSoup(credits_response.content, 'html.parser')

    # Extract directors from the table
    directors = []
    table = credits_soup.find('table', class_='simpleTable simpleCreditsTable')
    if table:
        for row in table.find_all('tr'):
            director_element = row.find('td', class_='name')
            if director_element:
                director_name = director_element.a.text.strip()
                directors.append(director_name)

    # Extract cast names
    cast_names = []
    cast_table = credits_soup.find("table", class_="cast_list")
    if cast_table:
        cast_td_elements = cast_table.find_all("td", class_=lambda value: value != "character")
        cast_names = [td.find("a").text.strip() for td in cast_td_elements if td.find("a")]
        cast_names = [name for name in cast_names if name]

    # Extract description
    description = soup.find('meta', {'name': 'description'}).get('content')

    # Construct the movie_details dictionary
    movie_details = {
        'Title': title,
        'Year': year,
        'Genre': genre,
        'Rating': rating,
        'Runtime': runtime,
        'Certificate': certificate,
        'Directors': directors,
        'Cast': cast_names,
        'Description': description
    }

    return movie_details
