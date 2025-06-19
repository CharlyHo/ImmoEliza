# Immoweb Scraper (Sitemap-based)

This project is a multi-threaded real estate data scraper for [Immoweb.be](https://www.immoweb.be), designed to collect structured property information and export it to a clean CSV file.

## ✅ Features

- Uses `cloudscraper` to bypass Cloudflare protection.
- Extracts property data directly from listing pages via embedded JavaScript (`window.classified`).
- Multi-threaded scraping for faster data collection.
- Handles data type conversions safely (e.g., int, float, bool).
- Outputs a structured CSV file with selected fields.

## 📦 Output

The output is saved to a file named:  
`immoweb_dataset.csv`

It includes the following columns:

- `Locality`
- `Type of property`
- `Price`
- `Number of rooms`
- `Living Area`
- `Garden`
- `Swimming pool`

## 🚀 How It Works

1. **Fetch Sitemaps:**  
   Scrapes Immoweb’s sitemap index to find sub-sitemaps containing listing URLs.

2. **Extract Property URLs:**  
   Parses all relevant property links (e.g. `https://www.immoweb.be/fr/annonce/...`).

3. **Scrape Individual Pages:**  
   For each property URL, extracts metadata embedded in the JavaScript using regex and parses the JSON.

4. **Save CSV:**  
   Stores all valid listings in a structured CSV file.

## 🧰 Requirements

- Python 3.7+
- Install dependencies:

```bash
pip install cloudscraper beautifulsoup4
