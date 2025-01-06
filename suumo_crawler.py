import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import time
import random
from datetime import datetime

class SuumoCrawler:
    def __init__(self):
        self.base_url = "https://suumo.jp"
        self.ua = UserAgent()
        self.headers = {
            'User-Agent': self.ua.random
        }
        
    def get_soup(self, url):
        """Make request with random delay and return BeautifulSoup object"""
        time.sleep(random.uniform(1, 3))  # Random delay between requests
        response = requests.get(url, headers=self.headers)
        response.encoding = 'utf-8'
        return BeautifulSoup(response.text, 'lxml')

    def parse_property_details(self, url):
        """Parse individual property page"""
        soup = self.get_soup(url)
        property_data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'title': soup.h1.text if soup.h1 else None,
            'rent': None,
            'location': None,
            'layout': None,
            'size': None,
            'building_age': None,
            'floor': None,
            'features': []
        }
        
        # Extract property details from table
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    header_text = header.text.strip()
                    value_text = value.text.strip()
                    
                    if '所在地' in header_text:
                        property_data['location'] = value_text
                    elif '間取り' in header_text:
                        property_data['layout'] = value_text
                    elif '専有面積' in header_text:
                        property_data['size'] = value_text
                    elif '築年数' in header_text:
                        property_data['building_age'] = value_text
                    elif '階' in header_text:
                        property_data['floor'] = value_text

        # Extract rent
        rent_text = soup.find('div', class_='property_view_main-emphasis')
        if rent_text:
            property_data['rent'] = rent_text.text.strip()

        # Extract features
        features_section = soup.find('h2', text='部屋の特徴・設備')
        if features_section:
            features_list = features_section.find_next('ul')
            if features_list:
                property_data['features'] = [feature.strip() for feature in features_list.text.split('、')]

        return property_data

    def crawl_listing_page(self, area_url):
        """Crawl a listing page and extract property URLs"""
        soup = self.get_soup(area_url)
        property_urls = []
        
        # Find all property links
        property_links = soup.find_all('a', href=True)
        for link in property_links:
            if '/chintai/jnc_' in link['href']:
                property_urls.append(self.base_url + link['href'])
            
        return property_urls

    def crawl_area(self, area_url, max_pages=3):
        """Crawl multiple pages for an area"""
        all_properties = []
        current_page = 1
        
        while current_page <= max_pages:
            page_url = f"{area_url}&page={current_page}" if current_page > 1 else area_url
            property_urls = self.crawl_listing_page(page_url)
            
            for url in property_urls:
                try:
                    property_data = self.parse_property_details(url)
                    all_properties.append(property_data)
                    print(f"Crawled: {url}")
                except Exception as e:
                    print(f"Error crawling {url}: {str(e)}")
            
            current_page += 1
            
        return all_properties

    def save_to_csv(self, properties, filename):
        """Save crawled data to CSV"""
        df = pd.DataFrame(properties)
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Saved {len(properties)} properties to {filename}")

def main():
    crawler = SuumoCrawler()
    
    # Example: Crawl properties in Shinjuku
    area_url = "https://suumo.jp/chintai/tokyo/sc_shinjuku/"
    properties = crawler.crawl_area(area_url, max_pages=3)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crawler.save_to_csv(properties, f'suumo_properties_{timestamp}.csv')

if __name__ == "__main__":
    main()
