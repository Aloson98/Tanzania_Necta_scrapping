# NECTA Results Scraper

## Overview

The **NECTA Results Scraper** is a Python-based program designed to scrape the National Examination Council of Tanzania (NECTA) results for advanced secondary school students and store the data in a MongoDB database. This project is developed for **educational purposes only**.

## Features

- Scrapes NECTA advanced secondary school results.
- Stores the extracted data efficiently in **MongoDB**.
- Provides tools for data analysis and visualization using **pandas, numpy, matplotlib, and seaborn**.
- Utilizes **BeautifulSoup** and **requests** for web scraping.

## Technologies Used

This project is implemented in **Python** and utilizes the following packages:

- **BeautifulSoup** – for parsing HTML data
- **requests** – for handling HTTP requests
- **mongoengine** – for interacting with MongoDB
- **pandas** – for data manipulation
- **numpy** – for numerical operations
- **matplotlib** – for data visualization
- **seaborn** – for advanced statistical plotting

## Installation

### Prerequisites

Ensure you have the following installed:

- **Python** (latest version recommended)
- **MongoDB** (for storing scraped results)

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Aloson98/Tanzania_Necta_scrapping.git
   cd NECTA-Scraper
   ```

2. Create a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # On macOS/Linux
   venv\Scripts\activate  # On Windows
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

## Usage

Inside collection, Run the scraper with the following command:

```bash
python main.py
```

Ensure that MongoDB is running before executing the script.

## Disclaimer

This program is strictly for **educational purposes** and should be used responsibly. Unauthorized scraping of websites may violate their terms of service.

## Contact

For any inquiries or contributions, feel free to reach out:
📧 **Email:** <graysonmwamafupa@yahoo.com>

## License

This project is licensed under the **MIT License** – see the LICENSE file for details.
