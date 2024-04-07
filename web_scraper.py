import concurrent.futures
import urllib.request
from bs4 import BeautifulSoup
import calendar
import os
import time
import pickle

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


def get_movies_per_date(year, month, cache_dir="cache"):
    """
    Get the number of movies released for each date in the specified month, and save the links in the specified format.

    Args:
    - year (int): The year for which to get the movies.
    - month (int): The month for which to get the movies.

    Returns:
    - movies_per_date (dict): A dictionary containing the number of movies released for each date in the month.
    """
    movies_per_date = {}
    num_days = calendar.monthrange(year, month)[1]
    month_dir = os.path.join("movies", str(year), str(month).zfill(2))
    os.makedirs(month_dir, exist_ok=True)

    for day in range(1, num_days + 1):
        date = f"{year}-{month:02d}-{day:02d}"
        base_url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={date},{date}&user_rating=1,10&genres=!documentary,!short&primary_language=en&adult=include"
        file_name = os.path.join(month_dir, f"{date}.txt")

        try:
            soup = fetch_page(base_url, cache_dir)
            tag = soup.find(class_='sc-fd6cf13d-3 genwjT')
            if tag:
                total_links_str = tag.text.split()[-1]
                total_links = int(total_links_str.replace(',', ''))
                movies_per_date[date] = total_links

                with open(file_name, 'w') as f:
                    pages = range(1, (total_links // 50) + 2)
                    with concurrent.futures.ThreadPoolExecutor() as executor:
                        for page_num, page_soup in zip(pages, executor.map(lambda p: fetch_page(f"{base_url}&page={p}", cache_dir), pages)):
                            a_tags = page_soup.find_all('a', class_="ipc-title-link-wrapper")
                            for a_tag in a_tags:
                                href_value = a_tag.get('href')
                                movie_id = href_value.split('/')[2]
                                movie_url = f'https://www.imdb.com/title/{movie_id}/'
                                f.write(movie_url + '\n')
            else:
                movies_per_date[date] = 0
        except Exception as e:
            print(f"An error occurred: {e}")

    return movies_per_date

month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

start_year = 2000
end_year = 2000
DIR = f'data'

os.makedirs(DIR, exist_ok=True)

start_time = time.time()

for year in range(start_year, end_year + 1):
    for month in month_dict:
        month_str = f"{month:02d}"
        movies_released = get_movies_per_date(year, month, cache_dir=os.path.join(DIR, "cache"))
        with open(f'{DIR}/movies_released_{year}.csv', 'a') as f:
            f.write(f'{month_dict[month]}: {sum(movies_released.values())}\n')

end_time = time.time()
runtime = end_time - start_time
print(f"Runtime: {runtime:.2f} seconds")