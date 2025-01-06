import requests
from bs4 import BeautifulSoup
import pandas as pd
from fake_useragent import UserAgent
import time
import random
import re
from datetime import datetime
from bs4.element import Tag as BeautifulSoupTag

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

    def clean_text(self, text):
        """Clean text by removing extra whitespace and newlines"""
        if not text:
            return ""
        return ' '.join(text.strip().split())

    def parse_property_details(self, url):
        """Parse individual property page"""
        soup = self.get_soup(url)
        property_data = {
            'url': url,
            'timestamp': datetime.now().isoformat(),
            'title': None,
            'rent': None,
            'location': None,
            'layout': None,
            'size': None,
            'building_age': None,
            'floor': None,
            'features': [],
            # Additional fields from 物件概要 and 物件詳細情報
            'layout_detail': None,      # 間取り詳細
            'structure': None,          # 構造
            'total_floors': None,       # 階建
            'construction_date': None,   # 築年月
            'parking': None,            # 駐車場
            'transaction_type': None,    # 取引態様
            'conditions': None,          # 条件
            'contract_period': None,     # 契約期間
            'guarantee_company': None,   # 保証会社
            'brokerage_fee': None,      # 仲介手数料
            'property_code': None,      # SUUMO物件コード
            'total_units': None,        # 総戸数
            'last_update': None,        # 情報更新日
            'insurance': None,          # 損保
            'entry_conditions': None,    # 入居
            'notes': None               # 備考
        }
        
        # Extract and clean title
        if soup.h1:
            title = self.clean_text(soup.h1.text)
            property_data['title'] = title

        # Extract property details from table
        tables = soup.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            for row in rows:
                header = row.find('th')
                value = row.find('td')
                if header and value:
                    header_text = header.text.strip()
                    value_text = self.clean_text(value.text)
                    
                    if '所在地' in header_text:
                        # Remove "地図を見る" from location
                        if value_text:
                            location = value_text.replace('地図を見る', '').strip()
                            property_data['location'] = location
                    elif '間取り' in header_text:
                        property_data['layout'] = value_text
                    elif '専有面積' in header_text:
                        # Extract only the number and unit
                        if value_text and 'm²' in value_text:
                            property_data['size'] = value_text
                    elif '築年数' in header_text:
                        property_data['building_age'] = value_text
                    elif '階建' in header_text:
                        property_data['total_floors'] = value_text
                        # Extract floor number from total_floors (e.g., "1階/2階建" -> "1階")
                        if '/' in value_text:
                            floor = value_text.split('/')[0]
                            property_data['floor'] = floor
                    elif '間取り' in header_text:
                        if not property_data.get('layout_detail'):  # Only set if not already set
                            property_data['layout_detail'] = value_text
                    elif '構造' in header_text:
                        property_data['structure'] = value_text
                    elif '築年月' in header_text:
                        property_data['construction_date'] = value_text
                    elif '駐車場' in header_text:
                        property_data['parking'] = value_text
                    elif '取引態様' in header_text:
                        property_data['transaction_type'] = value_text
                    elif '条件' in header_text:
                        property_data['conditions'] = value_text
                    elif '契約期間' in header_text:
                        property_data['contract_period'] = value_text
                    elif '保証会社' in header_text:
                        property_data['guarantee_company'] = value_text
                    elif '仲介手数料' in header_text:
                        property_data['brokerage_fee'] = value_text
                    elif 'SUUMO物件コード' in header_text or '物件コード' in header_text:
                        # Clean the property code value (remove any whitespace or special characters)
                        cleaned_code = ''.join(filter(str.isalnum, value_text))
                        if cleaned_code:
                            property_data['property_code'] = cleaned_code
                    elif '総戸数' in header_text:
                        property_data['total_units'] = value_text
                    elif '情報更新日' in header_text:
                        property_data['last_update'] = value_text
                    elif '損保' in header_text:
                        property_data['insurance'] = value_text
                    elif '入居' in header_text:
                        property_data['entry_conditions'] = value_text
                    elif '備考' in header_text:
                        property_data['notes'] = value_text

        # Extract rent - try different possible locations
        rent_text = None
        # Try to find rent in the main content
        rent_pattern = re.compile(r'(\d+\.?\d*)万円')
        for text in soup.stripped_strings:
            match = rent_pattern.search(text)
            if match:
                rent_text = match.group(0)
                break
                
        if rent_text:
            property_data['rent'] = rent_text
        
        # Extract size from title if not found in table
        if not property_data['size'] and property_data['title']:
            size_match = re.search(r'(\d+(?:\.\d+)?m²)', property_data['title'])
            if size_match:
                property_data['size'] = size_match.group(1)
                
        # Try to extract building age from different locations
        building_age = None
        # First try the dedicated fields
        for age_field in ['築年数', '築年月']:
            building_info = soup.find('th', string=re.compile(age_field))
            if building_info:
                td_element = building_info.find_next('td')
                if td_element and hasattr(td_element, 'text'):
                    building_age = td_element.text.strip()
                    if building_age:
                        break
        
        # If not found, try the title
        if not building_age:
            title = soup.find('h1')
            if title and hasattr(title, 'text'):
                age_pattern = re.compile(r'築(\d+)年')
                age_match = age_pattern.search(title.text)
                if age_match:
                    building_age = f"築{age_match.group(1)}年"
                    
        # If still not found, try searching all text
        if not building_age:
            for element in soup.find_all(['td', 'div', 'p']):
                if hasattr(element, 'text'):
                    text = element.text.strip()
                    if '築' in text:
                        age_pattern = re.compile(r'築(\d+)年')
                        age_match = age_pattern.search(text)
                        if age_match:
                            building_age = f"築{age_match.group(1)}年"
                            break
        
        if building_age:
            property_data['building_age'] = building_age

        # Extract features
        features = []
        # First try the dedicated section
        features_section = soup.find('h2', string='部屋の特徴・設備')
        if features_section:
            next_ul = features_section.find_next_sibling('ul')
            if next_ul and isinstance(next_ul, BeautifulSoupTag):
                for li in next_ul.find_all('li', recursive=False):
                    if li and hasattr(li, 'text'):
                        # Split by Japanese comma and filter out empty strings
                        item_features = [f.strip() for f in li.text.split('、') if f.strip()]
                        features.extend(item_features)
        
        # If no features found, try the table
        if not features:
            features_table = soup.find('th', string='設備')
            if features_table:
                td_element = features_table.find_next_sibling('td')
                if td_element and hasattr(td_element, 'text'):
                    features_text = td_element.text.strip()
                    features = [f.strip() for f in features_text.split('、') if f.strip()]
        
        # Remove duplicates while preserving order
        features = list(dict.fromkeys(features))
        
        property_data['features'] = features

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
        """Save crawled data to CSV with organized columns"""
        df = pd.DataFrame(properties)
        
        # Define column order to ensure consistent CSV structure
        columns = [
            'url', 'timestamp', 'title', 'rent', 'location',
            'layout', 'layout_detail', 'size', 'building_age',
            'construction_date', 'floor', 'total_floors',
            'structure', 'parking', 'transaction_type',
            'conditions', 'contract_period', 'guarantee_company',
            'brokerage_fee', 'property_code', 'total_units',
            'last_update', 'insurance', 'entry_conditions',
            'notes', 'features'
        ]
        
        # Ensure all columns exist, fill missing ones with empty strings
        for col in columns:
            if col not in df.columns:
                df[col] = ''
        
        # Reorder columns and save to CSV
        df = df[columns]
        df.to_csv(filename, index=False, encoding='utf-8-sig')
        print(f"Saved {len(properties)} properties to {filename}")

def main():
    crawler = SuumoCrawler()
    
    # Test crawl with a small sample
    area_url = "https://suumo.jp/chintai/tokyo/sc_shinjuku/"
    properties = crawler.crawl_area(area_url, max_pages=1)
    
    # Save results
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    crawler.save_to_csv(properties, f'suumo_properties_{timestamp}.csv')

if __name__ == "__main__":
    main()
