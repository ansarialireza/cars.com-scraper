# Cars.com Scraper

Welcome to the Cars.com Scraper, a Python script designed for efficient scraping of car information from the Cars.com website. This tool empowers you to gather comprehensive data about various car models, simplifying the process of analysis and comparison.

## Table of Contents
- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Example](#example)
- [Contributing](#contributing)
- [License](#license)

## Overview

Cars.com Scraper streamlines the collection of detailed information about different car models available on Cars.com. The script provides flexibility by supporting both serial and multithreaded implementations for efficient data retrieval.

## Features

- **Efficient Scraping:** Collects comprehensive information about cars, including make, model, year, and other details.
- **Serial and Multithreaded Scraping:** Supports both serial and multithreaded implementations for faster data extraction.
- **Customization:** Easily customize the script based on your requirements, such as specifying categories and URLs.
- **Summary Chart:** Generates a summary chart for the number of cars downloaded and execution time comparison.

## Requirements

Ensure you have the following prerequisites installed:

- **Python 3.x**
- **Requests library** (`requests`)
- **BeautifulSoup library** (`beautifulsoup4`)
- **Pandas library** (`pandas`)
- **Matplotlib library** (`matplotlib`)

You can install the dependencies using the provided `requirements.txt` file:

```bash
pip install -r requirements.txt
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone https://github.com/ansarialireza/cars.com-scraper.git
   ```

2. **Navigate to the project directory:**

   ```bash
   cd cars.com-scraper
   ```

3. **Install the required dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Run the script using the following command:

```bash
python cars_scraper.py
```

The script will perform both serial and multithreaded scraping of car information based on the specified categories and URLs.

## Example

```python
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
```

## Contributing

Contributions are welcome! Feel free to submit issues or pull requests to enhance the functionality of the scraper.

## License

This project is licensed under the [MIT License](LICENSE).