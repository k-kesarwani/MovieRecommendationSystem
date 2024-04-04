import os
import calendar
import time
import urllib.request
from bs4 import BeautifulSoup

def get_movies_per_date(year, month):
    """
    Get the number of movies released for each date in the specified month, and save the links in the specified format.

    Args:
        - year (int): The year for which to get the movies.
        - month (int): The month for which to get the movies.

    Returns:
        - movies_per_date (dict): A dictionary containing the number of movies released for each date in the month.
    """
    timeout_duration = 300  # 5 minutes
    movies_per_date = {}
    num_days = calendar.monthrange(year, month)[1]

    month_dir = os.path.join("movies", str(year), str(month).zfill(2))
    os.makedirs(month_dir, exist_ok=True)

    for day in range(1, num_days + 1):
        date = f"{year}-{month:02d}-{day:02d}"
        base_url = f"https://www.imdb.com/search/title/?title_type=feature&release_date={date},{date}&primary_language=en&adult=include"
        file_name = os.path.join(month_dir, f"{date}_links.txt")

        try:
            req = urllib.request.Request(base_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urllib.request.urlopen(req, timeout=timeout_duration)
            soup = BeautifulSoup(response, 'html.parser')
            tag = soup.find(class_='sc-fd6cf13d-3 genwjT')

            if tag:
                total_links_str = tag.text.split()[-1]
                total_links = int(total_links_str.replace(',', ''))  # Remove comma from the string
                movies_per_date[date] = total_links

                with open(file_name, 'w') as f:
                    for page_num in range(1, (total_links // 50) + 2):
                        url = f"{base_url}&page={page_num}"
                        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
                        response = urllib.request.urlopen(req, timeout=timeout_duration)
                        soup = BeautifulSoup(response, 'html.parser')
                        a_tags = soup.find_all('a', class_="ipc-title-link-wrapper")

                        for a_tag in a_tags:
                            href_value = a_tag.get('href')
                            movie_id = href_value.split('/')[2]
                            movie_url = f'https://www.imdb.com/title/{movie_id}/'
                            f.write(movie_url + '\n')
            else:
                movies_per_date[date] = 0

        except Exception as e:
            print(f"An error occurred: {e}")

        time.sleep(1)  # Add a short delay to avoid overwhelming the server

    return movies_per_date

def get_movie_details(movie_url):
    """
    Retrieves movie details from IMDb by scraping the provided URL.

    Args:
        movie_url (str): The URL of the IMDb movie page.

    Returns:
        dict: A dictionary containing the movie details, including title, year, rating,
              genre, runtime, director, cast, description, certificate, and URL.
    """
    req = urllib.request.Request(movie_url, headers={'User-Agent': 'Mozilla/5.0'})
    response = urllib.request.urlopen(req)
    soup = BeautifulSoup(response, 'html.parser')

    # Extract title, year of release, rating, and genre
    meta_tag = soup.find('meta', property='og:title')
    content = meta_tag.get('content')
    title_year, rating_genre = content.split('⭐')
    title, year = title_year.split('(')
    rating = float(rating_genre.split('|')[0].strip())
    genre = rating_genre.split('|')[1].strip()
    year = int(year.strip().strip(')'))

    # Extract runtime and certificate
    meta_tag = soup.find('meta', property='og:description')
    content = meta_tag.get('content')
    runtime_str, certificate = content.split('|')
    runtime_str = ''.join(filter(str.isdigit, runtime_str))
    runtime = int(runtime_str[0]) * 60 + int(runtime_str[1:])

    # Extract director
    director_meta = soup.find('meta', attrs={'name': 'description'})
    director = director_meta['content'].split(': Directed by ')[1].split('.')[0]

    # Extract cast
    cast_meta = soup.find('meta', attrs={'name': 'description'})
    cast = cast_meta['content'].split('With ')[1].split('.')[0]

    # Extract description
    description_meta = soup.find('meta', attrs={'name': 'description'})
    description = ' '.join(description_meta['content'].split('. ')[2:])

    movie_details = {
        'Title': title,
        'Year': year,
        'Rating': rating,
        'Genre': genre,
        'Runtime': runtime,
        'Director': director,
        'Cast': cast,
        'Description': description,
        'Certificate': certificate,
        'URL': movie_url
    }

    return movie_details