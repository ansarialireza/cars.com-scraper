import os
import requests
from bs4 import BeautifulSoup
import concurrent.futures
import pandas as pd
import time
import matplotlib.pyplot as plt
import random

class CarsScraper:

    def __init__(self, base_url, categories, max_pages=1):
        # Initialize the CarsScraper object with the provided base URL, categories, and maximum pages
        self.base_url = base_url
        self.categories = categories
        self.max_pages = max_pages if max_pages else {}
        
        # Initialize total_car_counts dictionary with each category and its count set to 0
        self.total_car_counts = {category: 0 for category in categories}
        
        # Initialize execution time variables for serial and multithreaded scraping
        self.serial_execution_time = 0
        self.multithreaded_execution_time = 0

    def send_request(self, url):
        try:
            # Send a GET request to the provided URL using the requests library
            response = requests.get(url)
            
            # Raise an exception for HTTP errors (status codes other than 2xx)
            response.raise_for_status()
            
            # Return the response object
            return response
        except requests.exceptions.RequestException as e:
            # Handle any request exceptions and print an error message
            print(f"Error: {e}")
            return None

    def parse_page(self, response):
        # Check if the response is valid and has a status code of 200 (OK)
        if response and response.status_code == 200:
            # Parse the HTML content of the response using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            
            # Return the BeautifulSoup object representing the parsed HTML
            return soup
        else:
            # Handle cases where the response is invalid or has a non-OK status code
            print(f"Error: Invalid response or status code {response}")
            return None


    def extract_car_info(self, car_element, category):
        # Initialize an empty dictionary to store car information
        car_info = {}

        try:
            # Extract the model year from the 'h2' element with class 'title'
            car_info['model_year'] = car_element.find('h2', class_='title').text.strip()

            # Extract the mileage information from the 'div' element with class 'mileage'
            mileage_element = car_element.find('div', class_='mileage')
            car_info['mileage'] = mileage_element.text.strip() if mileage_element else None

            # Extract the price information from the 'span' element with class 'primary-price'
            price_element = car_element.find('span', class_='primary-price')
            car_info['price'] = price_element.text.strip() if price_element else None

        except AttributeError as e:
            # Handle any attribute errors during extraction and print an error message
            print(f"Error extracting car information: {e}")

        # Add the 'category' key to the car_info dictionary
        car_info['category'] = category
        
        # Return the dictionary containing extracted car information
        return car_info


    def scrape_category(self, category, max_pages=None):
        # Set the maximum number of pages to scrape for the given category
        max_pages = max_pages or self.max_pages.get(category, 1)
        
        # Initialize an empty list to store car information
        car_info_list = []

        # Iterate through each page up to the specified maximum
        for page in range(1, max_pages + 1):
            # Construct the category-specific URL for the current page
            category_url = f"{self.base_url}&makes[]={category}&maximum_distance=all&page={page}&stock_type=all&zip="
            
            # Send a request to the constructed URL and get the response
            response = self.send_request(category_url)
            
            # Parse the HTML content of the response using BeautifulSoup
            soup = self.parse_page(response)

            # Check if the soup is valid
            if soup:
                # Extract car elements from the parsed HTML
                car_elements = soup.find_all('div', class_='vehicle-details')

                # Iterate through each car element and extract car information
                for car_element in car_elements:
                    car_info = self.extract_car_info(car_element, category)
                    car_info_list.append(car_info)

        # Update the total_car_counts dictionary with the total count for the given category
        self.total_car_counts[category] += len(car_info_list) // 2
        
        # Return the list of car information for the given category
        return car_info_list


    def save_metadata(self, car_info_list, category_folder):
        # Convert the list of car information into a Pandas DataFrame
        df = pd.DataFrame(car_info_list)

        # Define the path for the CSV file within the category folder
        csv_path = os.path.join(category_folder, 'car_info.csv')

        # Save the DataFrame as a CSV file without including the index column
        df.to_csv(csv_path, index=False)


    def scrape_cars_serial(self):
        # Record the start time of the serial execution
        start_time = time.time()

        # Iterate over each category and scrape car information sequentially
        for category in self.categories:
            # Scrape car information for the current category
            car_info_list = self.scrape_category(category)

            # Create a folder for each category in the 'output' directory
            category_folder = os.path.join('serial_output', category)
            os.makedirs(category_folder, exist_ok=True)

            # Save the metadata (car information) for the category in its respective folder
            self.save_metadata(car_info_list, category_folder)

        # Record the end time of the serial execution
        end_time = time.time()

        # Calculate and print the serial execution time
        self.serial_execution_time = end_time - start_time
        print(f"Serial Execution Time: {self.serial_execution_time:.2f} seconds")


    def scrape_cars_multithreaded(self):
        # Record the start time of the multithreaded execution
        start_time = time.time()

        # Create a ThreadPoolExecutor for concurrent multithreaded execution
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Submit scraping tasks for each category using ThreadPoolExecutor
            futures = [executor.submit(self.scrape_category, category) for category in self.categories]

            # Iterate over completed futures as they finish
            for future in concurrent.futures.as_completed(futures):
                # Retrieve the result of each completed future (car information list for a category)
                car_info_list = future.result()

                # Extract the category from the result
                category = car_info_list[0]['category']

                # Create a folder for each category in the 'output' directory
                category_folder = os.path.join('multithreaded_output', category)
                os.makedirs(category_folder, exist_ok=True)

                # Save the metadata (car information) for the category in its respective folder
                self.save_metadata(car_info_list, category_folder)

        # Record the end time of the multithreaded execution
        end_time = time.time()

        # Calculate and print the multithreaded execution time
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
# more categories >> 'acura','audi','cadillac','chevrolet','dodge','ford','honda','hyundai','infiniti','jaguar','bugatti','aston_martin','lexus'
        
categories = ['volvo', 'bmw', 'jeep', 'cadillac','acura','hyundai','ford','chevrolet']
url = "https://www.cars.com/shopping/results/?makes[]=volvo&maximum_distance=all&stock_type=all&zip="

# Example with max_pages
max_pages = {'volvo': 4, 'bmw': 8, 'jeep': 3, 'cadillac': 5,'acura':2,'hyundai':4,'ford':3,'chevrolet':8}

scraper = CarsScraper(url, categories, max_pages)

# Phase 1: Serial Implementation
scraper.scrape_cars_serial()

# Phase 2: Multithreaded Implementation
scraper.scrape_cars_multithreaded()

# Summary Chart
scraper.summary_chart()
