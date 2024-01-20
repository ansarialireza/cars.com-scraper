import requests
from bs4 import BeautifulSoup
import concurrent.futures
import time

class CarsScraper:
    def __init__(self, base_url, max_pages=10):
        self.base_url = base_url
        self.max_pages = max_pages

    def send_request(self, url):
        # Sends an HTTP GET request to the specified URL
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an HTTPError for bad responses
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None

    def parse_page(self, response):
        # Parses the HTML content of the response using BeautifulSoup
        if response and response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            return soup
        else:
            print(f"Error: Invalid response or status code {response.status_code}")
            return None

    def extract_car_info(self, car_element):
        # Extracts relevant information from a car element on the webpage
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

        return car_info

    def scrape_page(self, page_number):
        # Scrapes information from a specific page of the website
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
        # Scrapes car information using multiple threads for parallelization
        start_time = time.time()
        car_info_list = []

        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Use threads to parallelize scraping
            futures = [executor.submit(self.scrape_page, page_number) for page_number in range(1, self.max_pages + 1)]

            # Collect results from threads
            for future in concurrent.futures.as_completed(futures):
                car_info_list.extend(future.result())

        # Print car information
        for i, car_info in enumerate(car_info_list, start=1):
            self.print_car_info(i, car_info)

        end_time = time.time()
        return end_time - start_time

    def scrape_cars_without_threads(self):
        # Scrapes car information without using threads
        start_time = time.time()
        car_info_list = []

        for page_number in range(1, self.max_pages + 1):
            car_info_list.extend(self.scrape_page(page_number))

        # Print car information
        for i, car_info in enumerate(car_info_list, start=1):
            self.print_car_info(i, car_info)

        end_time = time.time()
        return end_time - start_time

    def print_car_info(self, index, car_info):
        # Prints the extracted car information
        print(f"\nCar {index}:\n{'=' * 30}")
        print(f"Model Year: {car_info['model_year']}")
        print(f"Mileage: {car_info['mileage']}")
        print(f"Price: {car_info['price']}")
        print(f"Price Drop: {car_info['price_drop']}")
        print(f"Dealer Rating: {car_info['dealer_rating']}")
        print('=' * 30)

# Example usage
url = "https://www.cars.com/shopping/results/?makes[]=&maximum_distance=30&models[]=&stock_type=all&zip="
scraper = CarsScraper(url, max_pages=2)

# Without threads
duration_without_threads = scraper.scrape_cars_without_threads()
print(f"Time without threads: {duration_without_threads} seconds")

# With threads
duration_with_threads = scraper.scrape_cars_with_threads()
print(f"Time with threads: {duration_with_threads} seconds")
