import concurrent.futures
from utils import fetch_page
import calendar
import os
import time

def get_movies_per_date(year, month, cache_dir="tmp/cache"):
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
    month_dir = os.path.join("movie_links", str(year), str(month).zfill(2))
    os.makedirs(month_dir, exist_ok=True)

    def write_url_to_file(file_name, url):
        with open(file_name, 'a') as f:
            f.write(url + '\n')

    for day in range(1, num_days + 1):
        date = f"{year}-{month:02d}-{day:02d}"
        base_url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={date},{date}&user_rating=1,10&genres=!documentary,!short&primary_language=en&adult=include"
        file_name = os.path.join(month_dir, f"{date}.txt")
        try:
            soup = fetch_page(base_url, cache_dir)
            a_tags = soup.find_all('a', class_='ipc-title-link-wrapper')
            total_links = len(a_tags)
            movies_per_date[date] = total_links
            if total_links != 0:
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    for a_tag in a_tags:
                        href_value = a_tag.get('href')
                        movie_id = href_value.split('/')[2]
                        movie_url = f'https://www.imdb.com/title/{movie_id}/'
                        executor.submit(write_url_to_file, file_name, movie_url)
                        
        except Exception as e:
            print(f"An error occurred: {e}")
            movies_per_date[date] = 0

    return movies_per_date

month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

start_year = 1990
end_year = 2023
DIR = f'tmp'
os.makedirs(DIR, exist_ok=True)

start_time = time.time()

for year in range(start_year, end_year + 1):
    for month in month_dict:
        month_str = f"{month:02d}"
        movies_released = get_movies_per_date(year, month)
        with open(f'{DIR}/movies_released_{year}.txt', 'a') as f:
            f.write(f'{month_dict[month]}: {sum(movies_released.values())}\n')

end_time = time.time()
runtime = end_time - start_time
print(f"Runtime: {runtime:.2f} seconds")