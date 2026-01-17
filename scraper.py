from curl_cffi import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.9",
    "Upgrade-Insecure-Requests": "1",
    "Sec-Ch-Ua": '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
    "Sec-Ch-Ua-Mobile": "?0",
    "Sec-Ch-Ua-Platform": '"Windows"',
}

def fetch_product_details(url):
    try:
        response = requests.get(url, headers=HEADERS, impersonate="chrome124", timeout=15)
        if response.status_code != 200:
            return None, None

        soup = BeautifulSoup(response.content, "html.parser")
        
        title_node = soup.find("span", {"id": "productTitle"}) or soup.find("h1", {"id": "title"})
        if not title_node:
            return None, None
            
        title = title_node.get_text().strip()

        price_node = soup.find("span", {"class": "a-price-whole"}) or soup.find("span", {"class": "a-offscreen"})
        if not price_node:
            return title, None

        price_text = price_node.get_text().replace("₹", "").replace(",", "").replace("$", "").strip()
        if price_text.endswith("."):
            price_text = price_text[:-1]
            
        return title, float(price_text)

    except Exception:
        return None, None