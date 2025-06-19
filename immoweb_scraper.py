import cloudscraper
from bs4 import BeautifulSoup
import json
import csv
import re
import concurrent.futures
import time

# Config
MAX_PROPERTIES = 10000
OUTPUT_FILE = "immoweb_dataset.csv"

# Setup Scraper
scraper = cloudscraper.create_scraper()

# Champs à extraire
CSV_FIELDS = [
    "Locality", "Type of property", "Price", "Number of rooms", 
    "Living Area", "Garden", "Swimming pool"
]

# Fonctions utilitaires
def safe_int(value):
    try:
        return int(value)
    except (TypeError, ValueError):
        return None

def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return None

def safe_bool(value):
    return bool(value) if value is not None else None

# Extraire URLs de propriétés
def get_property_urls():
    sitemap_index_url = "https://www.immoweb.be/sitemap.xml"
    response = scraper.get(sitemap_index_url)
    soup = BeautifulSoup(response.text, "xml")
    sitemap_links = [loc.text for loc in soup.find_all("loc") if "classified" in loc.text]

    print(f"[INFO] {len(sitemap_links)} sitemaps trouvés.")

    urls = set()
    for link in sitemap_links:
        try:
            r = scraper.get(link)
            sub_soup = BeautifulSoup(r.text, "xml")
            new_urls = {loc.text for loc in sub_soup.find_all("loc") if "/fr/annonce/" in loc.text}
            urls.update(new_urls)
            if len(urls) >= MAX_PROPERTIES:
                break
        except Exception as e:
            print(f"[ERREUR] Impossible de traiter {link} : {e}")
    
    print(f"[INFO] {len(urls)} URLs collectées.")
    return list(urls)[:MAX_PROPERTIES]

# Extraire données depuis une page
def extract_data_from_url(url):
    try:
        resp = scraper.get(url)
        soup = BeautifulSoup(resp.text, "html.parser")
        json_data = None
        for script in soup.find_all("script"):
            if script.string and "window.classified" in script.string:
                match = re.search(r"window\.classified\s*=\s*(\{.*?\});", script.string, re.DOTALL)
                if match:
                    json_data = json.loads(match.group(1))
                    break
        
        if not json_data:
            return None
        
        props = json_data.get("property", {})
        output = {
            "Locality": props.get("location", {}).get("locality"),
            "Type of property": props.get("type"),
            "Price": safe_float(props.get("price")),
            "Number of rooms": safe_int(props.get("bedroomCount")),
            "Living Area": safe_float(props.get("netHabitableSurface")),
            "Garden": safe_bool(props.get("hasGarden", False)),
            "Swimming pool": safe_bool(props.get("hasSwimmingPool", False)),
        }

        return output

    except Exception as e:
        print(f"[Erreur scraping] {url} : {e}")
        return None

# Multi-threaded scraping
def scrape_all(urls):
    results = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=20) as executor:
        for data in executor.map(extract_data_from_url, urls):
            if data:
                results.append(data)
            if len(results) >= MAX_PROPERTIES:
                break
    return results

# Écriture du CSV
def save_to_csv(data, filename):
    with open(filename, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        for row in data:
            writer.writerow(row)
    print(f"[✓] Données sauvegardées dans {filename}")

# Exécution
if __name__ == "__main__":
    start = time.time()
    urls = get_property_urls()
    dataset = scrape_all(urls)
    save_to_csv(dataset, OUTPUT_FILE)
    print(f"[✓] {len(dataset)} lignes extraites en {round(time.time() - start, 2)}s")
