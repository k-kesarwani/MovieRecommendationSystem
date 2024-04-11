import os
import utils
import mysql.connector

with open('sql_passkey.txt', 'r') as file: 
    pswd = file.read()

db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': pswd,
    'database': 'recommendation_system'
}

month_dict = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun', 7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}

start_year = 2016
end_year = 2023

# Establish database connection
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()

for year in range(start_year, end_year + 1):
    for month in month_dict:
        month_str = f"{month:02d}"
        for day in range(1, 32):
            day_str = f"{day:02d}"
            date_str = f"{year}-{month_str}-{day_str}"
            file_path = f'movie_links/{year}/{month_str}/{date_str}.txt'
            
            if os.path.exists(file_path):
                with open(file_path, 'r') as file:
                    urls = file.read().splitlines()
                
                batch_data = []
                for url in urls:
                    movie_details = utils.get_movie_details(url)
                    if movie_details:
                        title, year, genre, rating, runtime, certificate, directors, cast, description = movie_details.values()
                        batch_data.append((title, year, genre, rating, certificate, ', '.join(directors) if directors else None, ', '.join(cast) if cast else None, description, runtime))

                if batch_data:
                    # Define the SQL query to insert movie details
                    insert_query = """
                    INSERT INTO movies (Title, Year, Genre, Rating, Certificate, Directors, Cast, Description, Runtime)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    ON DUPLICATE KEY UPDATE
                        Year = VALUES(Year),
                        Genre = VALUES(Genre),
                        Rating = VALUES(Rating),
                        Certificate = VALUES(Certificate),
                        Directors = VALUES(Directors),
                        Cast = VALUES(Cast),
                        Description = VALUES(Description),
                        Runtime = VALUES(Runtime)
                    """

                    # Execute the SQL query in batches
                    cursor.executemany(insert_query, batch_data)
                    print(f"Finished processing {date_str}")
                    connection.commit()
            else:
                continue
connection.close()
