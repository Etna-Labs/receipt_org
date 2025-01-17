import requests
import os
from datetime import datetime
import time
import random

def fetch_reddit_thread(url):
    # Sophisticated browser-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1',
        'Referer': 'https://www.reddit.com/',
        'Cookie': ''  # Add any necessary cookies here
    }

    try:
        # Add random delay to appear more human-like
        time.sleep(random.uniform(2, 5))
        
        # Make the request
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            print(f'Successfully accessed the thread')
            print(f'Content length: {len(response.text)}')
        
            # Save the JSON content
            with open('wsb_thread.json', 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print('Thread content saved to wsb_thread.json')
            return True
        else:
            print(f'Failed to access thread. Status code: {response.status_code}')
            return False
        
        print(f'Thread content saved to wsb_thread.txt')
        
    except Exception as e:
        print(f'Error fetching thread: {str(e)}')

if __name__ == "__main__":
    url = "https://www.reddit.com/r/wallstreetbets/comments/1i2z5rd/what_are_your_moves_tomorrow_january_17_2025/.json"
    fetch_reddit_thread(url)
