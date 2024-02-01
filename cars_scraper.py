import os
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd
import time
import matplotlib.pyplot as plt
import random

class CarsScraper:
    def __init__(self, base_url, categories, max_pages=None):
        self.base_url = base_url
        self.categories = categories
        self.max_pages = max_pages if max_pages else {}
        self.total_car_counts = {category: 0 for category in categories}
        self.serial_execution_time = 0
        self.multithreaded_execution_time = 0

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
            print(f"Error: Invalid response or status code {response}")
            return None

    def extract_car_info(self, car_element, category):
        car_info = {}
        try:
            car_info['model_year'] = car_element.find('h2', class_='title').text.strip()

            mileage_element = car_element.find('div', class_='mileage')
            car_info['mileage'] = mileage_element.text.strip() if mileage_element else None

            price_element = car_element.find('span', class_='primary-price')
            car_info['price'] = price_element.text.strip() if price_element else None

            # Removed the section for extracting image URLs

        except AttributeError as e:
            print(f"Error extracting car information: {e}")

        car_info['category'] = category
        return car_info

    def scrape_category(self, category, max_pages=None):
        max_pages = max_pages or self.max_pages.get(category, 1)
        car_info_list = []

        for page in range(1, max_pages + 1):
            category_url = f"{self.base_url}&makes[]={category}&maximum_distance=all&page={page}&stock_type=all&zip="
            response = self.send_request(category_url)
            soup = self.parse_page(response)

            if soup:
                car_elements = soup.find_all('div', class_='vehicle-details')
                for car_element in car_elements:
                    car_info = self.extract_car_info(car_element, category)
                    car_info_list.append(car_info)

        # Update total_car_counts dictionary
        self.total_car_counts[category] += len(car_info_list) // 2
        return car_info_list

    def save_metadata(self, car_info_list, category_folder):
        # Removed the section for saving images

        # Generate CSV file
        df = pd.DataFrame(car_info_list)
        csv_path = os.path.join(category_folder, 'car_info.csv')
        df.to_csv(csv_path, index=False)

    def scrape_cars_serial(self):
        start_time = time.time()
        for category in self.categories:
            car_info_list = self.scrape_category(category)
            category_folder = os.path.join('output', category)
            os.makedirs(category_folder, exist_ok=True)
            self.save_metadata(car_info_list, category_folder)
        end_time = time.time()
        self.serial_execution_time = end_time - start_time
        print(f"Serial Execution Time: {self.serial_execution_time:.2f} seconds")

    def scrape_cars_multithreaded(self):
        start_time = time.time()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.scrape_category, category) for category in self.categories]

            for future in concurrent.futures.as_completed(futures):
                car_info_list = future.result()
                category = car_info_list[0]['category']
                category_folder = os.path.join('output', category)
                os.makedirs(category_folder, exist_ok=True)
                self.save_metadata(car_info_list, category_folder)
        end_time = time.time()
        self.multithreaded_execution_time = end_time - start_time
        print(f"Multithreaded Execution Time: {self.multithreaded_execution_time:.2f} seconds")

    def summary_chart(self, save_path='summary_chart.png'):
        # Plotting the combined chart
        categories = list(self.total_car_counts.keys())
        car_numbers = list(self.total_car_counts.values())

        fig, ax1 = plt.subplots(figsize=(10, 6))

        # Bar chart for car numbers with different colors for each category
        category_colors = {category: "#" + ''.join([random.choice('0123456789ABCDEF') for _ in range(6)]) for category in categories}
        colors = [category_colors[category] for category in categories]

        ax1.bar(categories, car_numbers, color=colors, alpha=0.7, label='Number of Cars')
        ax1.set_ylabel('Number of Cars', fontsize=12, color='black')
        ax1.tick_params('y', labelsize=10, colors='black')

        # Line chart for execution time comparison on the same plot
        ax2 = ax1.twinx()
        execution_times = [self.serial_execution_time, self.multithreaded_execution_time]
        ax2.plot(['Serial', 'Multithreaded'], execution_times, marker='o', color='red', label='Execution Time')
        ax2.set_ylabel('Execution Time (seconds)', fontsize=12, color='red')

        # Beautify the chart
        plt.title('Number of Cars Downloaded and Execution Time Comparison', fontsize=14)
        plt.xticks(rotation=45, ha='right', fontsize=12)
        plt.yticks(fontsize=12)
        ax1.legend(loc='upper left')
        ax2.legend(loc='upper right')

        # Save the chart
        plt.savefig(save_path, bbox_inches='tight')
        print(f"Summary chart saved to {save_path}")

        # Display the chart
        plt.show()


# Example usage
categories = ['volvo', 'bmw', 'jeep', 'mercedes_benz']
url = "https://www.cars.com/shopping/results/?makes[]=volvo&maximum_distance=all&stock_type=all&zip="

# Example with max_pages
max_pages = {'volvo': 3, 'bmw': 1, 'jeep': 2, 'mercedes_benz': 4}
scraper = CarsScraper(url, categories, max_pages)

# Phase 1: Serial Implementation
scraper.scrape_cars_serial()

# Phase 2: Multithreaded Implementation
scraper.scrape_cars_multithreaded()

# Summary Chart
scraper.summary_chart()