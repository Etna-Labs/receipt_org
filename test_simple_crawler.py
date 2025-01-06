import time
from simple_suumo_crawler import SimpleSuumoCrawler
import json

def test_crawler():
    url = "https://suumo.jp/ms/chuko/tokyo/sc_shibuya/nc_76595753/"
    
    # Initialize crawler
    crawler = SimpleSuumoCrawler()
    
    # Measure execution time
    start_time = time.time()
    
    # Extract data
    data = crawler.extract_property_details(url)
    
    # Calculate execution time
    execution_time = time.time() - start_time
    
    # Print results
    print(f"\nExecution time: {execution_time:.2f} seconds")
    print("\nExtracted Data:")
    print(json.dumps(data, ensure_ascii=False, indent=2))
    
    # Define expected fields based on header mapping
    expected_fields = [
        'price', 'location', 'access', 'layout', 'size',
        'building_age', 'management_fee', 'repair_reserve',
        'floor_structure', 'total_units', 'property_name',
        'address', 'direction', 'units_for_sale', 'other_area',
        'floor', 'building_structure'
    ]
    
    # Print detailed data report
    print("\nExtracted Fields:")
    for key, value in sorted(data.items()):
        print(f"- {key}: {value}")
    
    # Calculate coverage
    filled_fields = [field for field in expected_fields if field in data and data[field]]
    coverage = (len(filled_fields) / len(expected_fields)) * 100
    
    print(f"\nCoverage Report:")
    print(f"Expected fields: {len(expected_fields)}")
    print(f"Found fields: {len(filled_fields)}")
    print(f"Coverage: {coverage:.1f}%")
    
    print("\nMissing Fields:")
    missing_fields = [field for field in expected_fields if field not in data or not data[field]]
    for field in missing_fields:
        print(f"- {field}")
    
    # Save to CSV
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    filename = f"suumo_property_{timestamp}.csv"
    crawler.save_to_csv(data, filename)
    print(f"\nData saved to {filename}")

if __name__ == "__main__":
    test_crawler()
