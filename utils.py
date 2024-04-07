import os
import urllib
from bs4 import BeautifulSoup

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
    try:
        response = urllib.request.urlopen(req)
        soup = BeautifulSoup(response, 'html.parser')

        # Extract title, year of release, rating, and genre
        meta_tag = soup.find('meta', property='og:title')
        if meta_tag:
            content = meta_tag.get('content')
            title_year, rating_genre = content.split('⭐')
            title = title_year.split()[:-1]
            title = ' '.join(title)
            year = title_year.split()[-1]
            year = int(year.strip('(').strip(')'))
            rating = float(rating_genre.split('|')[0].strip())
            genre = rating_genre.split('|')[1].strip()
        else:
            title = None
            year = None
            rating = None
            genre = None

        # Extract runtime and certificate
        meta_tag = soup.find('meta', property='og:description')
        if meta_tag:
            content = meta_tag.get('content')
            if '|' in content:
                runtime_str, certificate = content.split('|')
                runtime_str = ''.join(filter(str.isdigit, runtime_str))
                runtime = int(runtime_str[0]) * 60 + int(runtime_str[1:])
            else:
                content = ''.join(filter(str.isdigit, content))
                runtime = int(content[0]) * 60 + int(content[1:])
                certificate = None
        else:
            runtime = None
            certificate = None

        # Extract director
        description_meta = soup.find('meta', attrs={'name': 'description'})
        if description_meta and 'Directed by ' in description_meta['content']:
            director = description_meta['content'].split(': Directed by ')[1].split('.')[0]
        else:
            director = None

        # Extract cast
        if description_meta:
            cast = description_meta['content'].split('With ')[1].split('.')[0]
        else:
            cast = None

        # Extract description
        if description_meta:
            description = ' '.join(description_meta['content'].split('. ')[2:])
        else:
            description = None

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
    except (urllib.error.URLError, ValueError, IndexError, AttributeError):
        return None
    
def monthly_links(year, month, output_file):
    """
    Combines all the movie links from the individual files for the specified year and month
    into a single file named '{year}-{month:02d}_links.txt'. After that, it deletes the
    individual files.

    Args:
        year (int): The year for which to combine the links.
        month (int): The month for which to combine the links.

    Returns:
        None
    """
    month_str = f"{month:02d}"

    # Combine links into a single file
    links = []
    for day in range(1, 32):
        day_str = f"{day:02d}"
        file_path = f"movies/{year}/{month_str}/{year}-{month_str}-{day_str}_links.txt"
        if os.path.exists(file_path):
            with open(file_path, 'r') as file:
                links.extend(file.read().splitlines())
            print(f"Wrote links from {file_path} to '{output_file}'")
        else:
            print(f"No file found for {year}-{month_str}-{day_str}")

    with open(output_file, 'w') as fo:
        fo.write('\n'.join(links))

    # # Delete individual files
    # for day in range(1, 32):
    #     day_str = f"{day:02d}"
    #     file_path = f"movies/{year}/{month_str}/{year}-{month_str}-{day_str}_links.txt"
    #     if os.path.exists(file_path):
    #         os.remove(file_path)
    #         print(f"Deleted {file_path}")

    # print("All individual files deleted.")