import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time
import pandas as pd
from tabulate import tabulate

class CarsScraper:
    def __init__(self, base_url, max_pages=10):
        self.base_url = base_url
        self.max_pages = max_pages

    def send_request(self, url):
        try:
            response = requests.get(url)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def parse_page(self, response):
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"Error: Invalid response or status code {response.status_code}")
            return None

    def extract_car_info(self, car_element):
        car_info = {}
        try:
            car_info['model_year'] = car_element.find('h2', class_='title').text.strip()
            mileage_element = car_element.find('div', class_='mileage')
            car_info['mileage'] = mileage_element.get_text(strip=True) if mileage_element else "N/A"
            car_info['price'] = car_element.find('span', class_='primary-price').text.strip()
            price_drop_element = car_element.find('span', class_='price-drop')
            car_info['price_drop'] = price_drop_element.text.strip() if price_drop_element else "N/A"
            dealer_rating_element = car_element.find('span', class_='sds-rating__count')
            car_info['dealer_rating'] = dealer_rating_element.text.strip() if dealer_rating_element else "N/A"
        except AttributeError as e:
            print(f"Error extracting car information: {e}")

        keys_to_check = ['model_year', 'mileage', 'price', 'price_drop', 'dealer_rating']
        for key in keys_to_check:
            car_info.setdefault(key, "N/A")

        return car_info

    def scrape_page(self, page_number):
        page_url = f"{self.base_url}&page={page_number}"
        response = self.send_request(page_url)
        soup = self.parse_page(response)

        car_info_list = []

        if soup:
            car_elements = soup.find_all('div', class_='vehicle-details')
            for car_element in car_elements:
                car_info = self.extract_car_info(car_element)
                car_info_list.append(car_info)

        return car_info_list

    def scrape_cars_with_threads(self):
        start_time = time.time()
        car_info_list = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.scrape_page, page_number) for page_number in range(1, self.max_pages + 1)]

            for future in concurrent.futures.as_completed(futures):
                car_info_list.extend(future.result())

        end_time = time.time()
        duration = end_time - start_time

        return duration, car_info_list

    def scrape_cars_without_threads(self):
        start_time = time.time()
        car_info_list = []

        for page_number in range(1, self.max_pages + 1):
            car_info_list.extend(self.scrape_page(page_number))

        end_time = time.time()
        duration = end_time - start_time

        return duration, car_info_list
    
    def save_to_excel(self, car_info_list, file_path='car_info.xlsx'):
        try:
            df = pd.DataFrame(car_info_list)
            df.to_excel(file_path, index=False)
            # print(f"Car information saved to {file_path}")
        except Exception as e:
            print(f"Error saving car information to Excel: {e}")

    def format_duration(self, duration):
        minutes, seconds = divmod(duration, 60)
        return f"{int(minutes)} minutes and {seconds:.2f} seconds"

    def display_results(self, label, duration, car_info_list, file_path):
        print(f"\nResults {label}:")
        print(f"Time taken: {self.format_duration(duration)}")
        print(f"Number of cars scraped: {len(car_info_list)}")
        print(f"Saved car information to {file_path}")

    def display_results_table(self, durations, num_cars, file_paths):
        headers = ["Results", "Time taken", "Number of cars scraped", "Saved file"]
        data = [
            ["Without Threads", durations[0], num_cars[0], file_paths[0]],
            ["With Threads", durations[1], num_cars[1], file_paths[1]],
        ]
        table = tabulate(data, headers, tablefmt="pretty")
        print(table)

# Example usage
url = "https://www.cars.com/shopping/results/?makes[]=&maximum_distance=30&models[]=&stock_type=all&zip="

scraper = CarsScraper(url, max_pages=5)

# Without threads
duration_without_threads, car_info_list_without_threads = scraper.scrape_cars_without_threads()
scraper.save_to_excel(car_info_list_without_threads, file_path='car_info_without_threads.xlsx')
# scraper.display_results("Without Threads", duration_without_threads, car_info_list_without_threads, 'car_info_without_threads.xlsx')

# With threads
duration_with_threads, car_info_list_with_threads = scraper.scrape_cars_with_threads()
scraper.save_to_excel(car_info_list_with_threads, file_path='car_info_with_threads.xlsx')
# scraper.display_results("With Threads", duration_with_threads, car_info_list_with_threads, 'car_info_with_threads.xlsx')

# Summary table
scraper.display_results_table([duration_without_threads, duration_with_threads],
                              [len(car_info_list_without_threads), len(car_info_list_with_threads)],
                              ['car_info_without_threads.xlsx', 'car_info_with_threads.xlsx'])
