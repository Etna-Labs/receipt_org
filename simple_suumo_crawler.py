import requests
from bs4 import BeautifulSoup, Tag
import pandas as pd
from datetime import datetime
import re

class SimpleSuumoCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        # Initialize data dictionary with default values
        self.data = {
            'url': '',
            'timestamp': '',
            'property_name': '',
            'price': '',
            'layout': '',
            'size': '',
            'building_age': '',
            'location': '',
            'access': '',
            'total_units': '',
            'floor': '',
            'building_structure': '',
            'management_fee': '',
            'repair_reserve': '',
            'other_area': '',
            'units_for_sale': '',
            'direction': '',
            'floor_structure': ''
        }
        
        # Initialize header mappings for both sections
        self.header_mapping = {
            '価格': 'price',
            '価格ヒント': 'price',
            '所在地': 'location',
            '交通': 'access',
            'アクセス': 'access',
            '交通ヒント': 'access',
            '間取り': 'layout',
            '間取りヒント': 'layout',
            '専有面積': 'size',
            '専有面積ヒント': 'size',
            '築年数': 'building_age',
            '築年月': 'building_age',
            '建築年月': 'building_age',
            '完成時期': 'building_age',
            '完成時期（築年月）': 'building_age',
            '築年数ヒント': 'building_age',
            '管理費': 'management_fee',
            '管理費等': 'management_fee',
            '管理費ヒント': 'management_fee',
            '修繕積立金': 'repair_reserve',
            '修繕積立金ヒント': 'repair_reserve',
            '階数': 'floor',
            '所在階': 'floor',
            '所在階/構造・階建': 'floor_structure',
            '所在階/構造・階建ヒント': 'floor_structure',
            '構造': 'building_structure',
            '構造・階建て': 'building_structure',
            '構造ヒント': 'building_structure',
            '総戸数': 'total_units',
            '総戸数ヒント': 'total_units',
            '物件名': 'property_name',
            'マンション名': 'property_name',
            '住所': 'address',
            '方位': 'direction',
            '向き': 'direction',
            '方位ヒント': 'direction',
            '販売戸数': 'units_for_sale',
            '販売戸数ヒント': 'units_for_sale',
            'その他面積': 'other_area',
            'その他面積ヒント': 'other_area',
            '取引態様': 'transaction_type',
            '引渡可能時期': 'delivery_date'
        }
        
        # Special field processors for complex data
        self.field_processors = {
            'floor_structure': lambda x: self._process_floor_structure(x),
            'price': lambda x: self._process_price(x),
            'size': lambda x: self._process_size(x),
            'building_age': lambda x: self._process_building_age(x),
            'access': lambda x: self._process_access(x),
            'layout': lambda x: self._process_layout(x)
        }
        
    def _process_building_age(self, value):
        """Extract and standardize building age information"""
        value = self.clean_value(value)
        # Try to extract year and month
        year_month = re.search(r'(\d{4})年(\d{1,2})月', value)
        if year_month:
            return f"{year_month.group(1)}年{year_month.group(2)}月"
        # Try to extract years since built
        years = re.search(r'築(\d+)年', value)
        if years:
            return f"築{years.group(1)}年"
        # Try to extract completion date
        completion = re.search(r'(\d{4})年', value)
        if completion:
            return f"{completion.group(1)}年"
        return value
        
    def _process_access(self, value):
        """Clean up and standardize access information"""
        value = self.clean_value(value)
        # Extract station and walking time
        access_info = []
        for line in value.split('\n'):
            line = line.strip()
            if not line:
                continue
            # Match patterns like "東急東横線「代官山」歩3分"
            match = re.search(r'(.+線「.+」)歩(\d+)分', line)
            if match:
                access_info.append(f"{match.group(1)}徒歩{match.group(2)}分")
            else:
                access_info.append(line)
        return ' / '.join(access_info)
        
    def _process_layout(self, value):
        """Clean up and standardize layout information"""
        value = self.clean_value(value)
        # Extract basic layout (e.g., 2LDK)
        layout_match = re.search(r'([0-9]+[SLDK]+)', value)
        if layout_match:
            return layout_match.group(1)
        return value
        
    def _process_floor_structure(self, value):
        """Extract floor and structure information"""
        value = self.clean_value(value)
        if '/' in value:
            floor, structure = value.split('/', 1)
            return {
                'floor': re.sub(r'[^\d]', '', floor),
                'building_structure': structure.strip()
            }
        return value
        
    def _process_price(self, value):
        """Clean up price information"""
        value = self.clean_value(value)
        # Remove any text after space (like "支払シミュレーション")
        value = value.split()[0]
        # Extract the numeric part and unit
        match = re.search(r'(\d+(?:\.\d+)?)(億)?(\d*(?:\.\d+)?)?万?円?', value)
        if match:
            amount = float(match.group(1) or 0)
            if match.group(2):  # Has 億
                amount = amount * 10000  # Convert 億 to 万
            if match.group(3):  # Additional 万
                amount += float(match.group(3) or 0)
            return f"{amount}万円"
        return value
        
    def _process_size(self, value):
        """Clean up size information"""
        value = self.clean_value(value)
        # Extract the numeric part with unit
        match = re.search(r'(\d+(?:\.\d+)?)\s*m2', value)
        if match:
            return f"{match.group(1)}m²"
        return value
        
    def clean_value(self, value):
        """Clean up value text by removing extra information in brackets"""
        value = self.clean_text(value)
        # Remove text in square brackets
        value = re.sub(r'\[.*?\]', '', value)
        # Remove text after specific markers
        markers = ['□', '■', '【', '※']
        for marker in markers:
            if marker in value:
                value = value.split(marker)[0]
        return value.strip()

    def clean_text(self, text):
        """Clean up text by removing extra whitespace, newlines, and special characters"""
        if not text:
            return ""
        # Remove common suffixes that might prevent header matching
        text = text.replace('ヒント', '')
        # Remove any text in parentheses
        text = re.sub(r'[\(（].*?[\)）]', '', text)
        # Remove special characters but keep Japanese text
        text = re.sub(r'[^\w\s\u3000-\u9fff]', '', text)
        # Normalize whitespace
        text = ' '.join(text.split())
        # Strip any remaining whitespace
        return text.strip()

    def extract_property_details(self, url):
        response = requests.get(url, headers=self.headers)
        print(f"\nResponse status code: {response.status_code}")
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        data = {
            'url': url,
            'timestamp': datetime.now().isoformat()
        }

        # Debug: Print the HTML structure
        print("\nHTML Structure:")
        print(soup.prettify()[:1000])  # Print first 1000 chars to see structure
        
        print("\nSearching for sections...")
        
        # Find sections by their h3 headers and process their tables
        section_mapping = {
            '物件詳細情報': ['物件詳細情報', '詳細情報'],  # Multiple possible titles
            '物件概要': ['物件概要', '共通概要', '概要']  # Multiple possible titles
        }
        
        print("\nAll h3 elements on the page:")
        all_h3s = soup.find_all('h3')
        for h3 in all_h3s:
            print(f"- {h3.get_text(strip=True)}")
        
        for section_title, actual_title in section_mapping.items():
            print(f"\nLooking for section: {actual_title}")
            
            # Find all h3 elements and print them for debugging
            h3_elements = soup.find_all('h3')
            print(f"Found {len(h3_elements)} h3 elements:")
            for h3 in h3_elements:
                print(f"H3 text: '{h3.get_text(strip=True)}'")
            
            # Find the correct section
            section_h3 = None
            for h3 in h3_elements:
                h3_text = h3.get_text(strip=True)
                print(f"Checking h3: '{h3_text}'")
                # Check if any of the possible titles match
                if isinstance(actual_title, list):
                    if any(title in h3_text for title in actual_title):
                        section_h3 = h3
                        print(f"Found section with title variant: {h3_text}")
                        break
                elif actual_title in h3_text:
                    section_h3 = h3
                    print(f"Found matching section: '{h3_text}'")
                    break
            
            if section_h3:
                # Debug: Print HTML structure after h3
                print(f"\nHTML structure after {h3_text}:")
                next_sibling = section_h3.find_next_sibling()
                if next_sibling:
                    print(next_sibling.prettify()[:500])
                
                # Find and process the table
                print("\nSearching for table...")
                print(f"\nSearching for tables associated with section {h3_text}")
                
                # Find all tables between this h3 and the next h3
                next_h3 = section_h3.find_next('h3')
                tables = []
                
                # Get all tables after this h3
                current_table = section_h3.find_next('table')
                while current_table:
                    # Stop if we hit the next h3
                    prev_h3 = current_table.find_previous('h3')
                    if next_h3 and (prev_h3 != section_h3 and prev_h3.find_previous('h3') != section_h3):
                        break
                    tables.append(current_table)
                    print(f"\nProcessing table in section {h3_text}:")
                    
                    # Process each row in the table
                    for row in current_table.find_all('tr'):
                        headers = row.find_all('th')
                        values = row.find_all('td')
                        
                        # Process each header-value pair in the row
                        for header, value in zip(headers, values):
                            header_text = self.clean_text(header.get_text())
                            value_text = self.clean_text(value.get_text())
                            print(f"Header: {header_text}, Value: {value_text}")
                            
                            # Map Japanese headers to English field names
                            if '物件名' in header_text:
                                data['property_name'] = value_text
                            elif '価格' in header_text:
                                data['price'] = self._process_price(value_text)
                            elif '間取り' in header_text:
                                data['layout'] = self._process_layout(value_text)
                            elif '専有面積' in header_text:
                                data['size'] = self._process_size(value_text)
                            elif '所在階' in header_text and '構造・階建' in header_text:
                                floor_info = self._process_floor_structure(value_text)
                                if isinstance(floor_info, dict):
                                    for k, v in floor_info.items():
                                        data[k] = v
                            elif '完成時期' in header_text or '築年月' in header_text:
                                data['building_age'] = self._process_building_age(value_text)
                            elif '住所' in header_text:
                                data['location'] = value_text
                            elif '交通' in header_text:
                                data['access'] = self._process_access(value_text)
                            elif '管理費' in header_text:
                                data['management_fee'] = value_text
                            elif '修繕積立金' in header_text:
                                data['repair_reserve'] = value_text
                            elif 'その他面積' in header_text:
                                data['other_area'] = value_text
                            elif '総戸数' in header_text:
                                data['total_units'] = value_text
                            elif '販売戸数' in header_text:
                                data['units_for_sale'] = value_text
                    
                    current_table = current_table.find_next('table')
                
                print(f"Found {len(tables)} tables in section {h3_text}")
                    
                if not section_h3:
                    print(f"Section {actual_title} not found")
                    continue
            
            # Debug: Print current data state after processing section
            print(f"\nCurrent data after processing {actual_title}:")
            for k, v in data.items():
                print(f"- {k}: {v}")

        return data

    def save_to_csv(self, data, filename):
        df = pd.DataFrame([data])
        df.to_csv(filename, index=False, encoding='utf-8')
        print(f"Data saved to {filename}")

def main():
    url = "https://suumo.jp/ms/chuko/tokyo/sc_shibuya/nc_76595753/"
    crawler = SimpleSuumoCrawler()
    data = crawler.extract_property_details(url)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"suumo_property_{timestamp}.csv"
    crawler.save_to_csv(data, filename)
    print("Extracted data:", data)

if __name__ == "__main__":
    main()
