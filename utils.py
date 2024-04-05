import os

def combine_and_delete_monthly_links(year, month):
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
    output_file = f"{year}-{month_str}_links.txt"

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

    print(f'Done writing {len(links)} links to {output_file}')

    # Delete individual files
    for day in range(1, 32):
        day_str = f"{day:02d}"
        file_path = f"movies/{year}/{month_str}/{year}-{month_str}-{day_str}_links.txt"
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"Deleted {file_path}")

    print("All individual files deleted.")