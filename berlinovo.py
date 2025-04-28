import requests
from bs4 import BeautifulSoup
import json
from datetime import datetime
import os
import time
from typing import Dict, List

class BerlinovoTracker:
    def send_notification(self, title, message):
        print(f"Sending notification: {title} - {message}")
        bot_token = os.environ.get("TELEGRAM_BERLINOVO_BOT_TOKEN")
        chat_id = os.environ.get("TELEGRAM_BERLINOVO_CHAT_ID")
        if bot_token and chat_id:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {"chat_id": chat_id, "text": f"{title}\n{message}"}
            requests.post(url, data=data)
            print("Telegram notification sent successfully.")
        else:
            print("Telegram credentials not set. Notification not sent.")

    def __init__(self):
        self.base_url = "https://www.berlinovo.de"
        self.search_url = "https://www.berlinovo.de/de/wohnungen/suche"
        self.data_file = "apartment_listings.json"
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }

    def fetch_listings(self) -> List[Dict]:
        try:
            response = requests.get(self.search_url, headers=self.headers)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')
            
            listings = []
            # Find all apartment listings - they appear to be in article elements
            apartment_elements = soup.find_all('article')
            
            for apt in apartment_elements:
                # Extract title and URL from the nested structure
                title_element = apt.find('div', class_='title')
                title_link = title_element.find('a') if title_element else None
                
                # Get the address - it's usually in a div with class 'address' or similar
                address_element = apt.find('span', class_='address-line1')
                
                # Get price information - updated to match the actual HTML structure
                price_field = apt.find('div', class_='field--name-field-total-rent')
                price_value = None
                if price_field:
                    price_item = price_field.find('div', class_='field__item')
                    if price_item:
                        price_value = price_item.text.strip()
                
                # Get size information
                size_element = apt.find('div', class_='size')
                
                # Get rooms information
                rooms_element = apt.find('div', class_='rooms')
                
                listing = {
                    'id': apt.get('data-id', ''),
                    'title': title_link.text.strip() if title_link else '',
                    'url': self.base_url + title_link['href'] if title_link and 'href' in title_link.attrs else '',
                    'address': address_element.text.strip() if address_element else '',
                    'price': price_value,
                    'size': size_element.text.strip() if size_element else '',
                    'rooms': rooms_element.text.strip() if rooms_element else '',
                    'timestamp': datetime.now().isoformat()
                }
                listings.append(listing)
            
            return listings
        except Exception as e:
            print(f"Error fetching listings: {e}")
            return []

    def load_previous_listings(self) -> List[Dict]:
        if os.path.exists(self.data_file):
            with open(self.data_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []

    def save_listings(self, listings: List[Dict]):
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(listings, f, ensure_ascii=False, indent=2)

    def find_new_listings(self, current_listings: List[Dict], previous_listings: List[Dict]) -> List[Dict]:
        previous_ids = {listing['id'] for listing in previous_listings}
        return [listing for listing in current_listings if listing['id'] not in previous_ids]

    def track_listings(self):
        start_time = datetime.now()
        print(f"Starting Berlinovo apartment tracker at {start_time.strftime('%Y-%m-%d %H:%M:%S')}...")
        

        self.send_notification("Test Notification", "This is a test notification to check if notifications are working.")
        
        while True:
            try:
                current_time = datetime.now()
                print(f"\nChecking for new listings at {current_time.strftime('%Y-%m-%d %H:%M:%S')}...")
                
                current_listings = self.fetch_listings()
                previous_listings = self.load_previous_listings()
                
                new_listings = self.find_new_listings(current_listings, previous_listings)
                
                filtered_listings = [listing for listing in new_listings if "Christoph" in listing['address']]

                if filtered_listings:
                    print(f"\nFound {len(filtered_listings)} new listings!")
                    for listing in filtered_listings:
                        print(f"\nNew Apartment Found:")
                        print(f"Title: {listing['title']}")
                        print(f"Address: {listing['address']}")
                        print(f"Price: {listing['price']}")
                        print(f"Size: {listing['size']}")
                        print(f"Rooms: {listing['rooms']}")
                        print(f"URL: {listing['url']}")
                        print("-" * 50)

                   # Send desktop notification using osascript
                    self.send_notification(
                        "New Apartment Listings Found!",
                        f"Found {len(filtered_listings)} new listings with 'Fischerinsel' in the address!"
                    )

                    # notification.notify(
                    #     title="New Apartment Listings Found!",
                    #     message=f"Found {len(filtered_listings)} new listings with 'Fischerinsel' in the address!",
                    #     app_icon=None,  # e.g. 'C:\\icon_32x32.ico'
                    #     timeout=10  # seconds
                    # )
                
                self.save_listings(current_listings)
                
                # Wait for 5 minutes before checking again
                print("\nWaiting 5 minutes before next check...")
                time.sleep(300)
                
            except Exception as e:
                print(f"Error in tracking loop: {e}")
                time.sleep(60)  # Wait a minute before retrying if there's an error

    def debug_listings(self):
        """Debug method to print raw HTML structure"""
        response = requests.get(self.search_url, headers=self.headers)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Print the first article's HTML structure
        first_article = soup.find('article')
        if first_article:
            print("First article HTML structure:")
            print(first_article.prettify())
        else:
            print("No articles found")

if __name__ == "__main__":
    tracker = BerlinovoTracker()
    tracker.track_listings()
    tracker.debug_listings()
