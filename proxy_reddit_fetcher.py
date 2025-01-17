import requests
from bs4 import BeautifulSoup
import random
import time

def get_thread_content(url):
    # Browser-like headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9',
        'Accept-Encoding': 'gzip, deflate, br',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1',
        'Cache-Control': 'max-age=0',
        'DNT': '1'
    }
    
    # Free proxy list (these are example proxies, they may not work)
    proxies = [
        'http://34.23.45.223:80',
        'http://165.227.71.60:80',
        'http://157.245.207.236:80'
    ]
    
    for proxy in proxies:
        try:
            print(f"Trying proxy: {proxy}")
            proxy_dict = {
                'http': proxy,
                'https': proxy
            }
            
            # Add some randomized delay to appear more human-like
            time.sleep(random.uniform(1, 3))
            
            response = requests.get(
                url,
                headers=headers,
                proxies=proxy_dict,
                timeout=10
            )
            
            if response.status_code == 200:
                print("Successfully accessed the thread!")
                # Save the content
                with open('wsb_thread.html', 'w', encoding='utf-8') as f:
                    f.write(response.text)
                return True
            
        except Exception as e:
            print(f"Error with proxy {proxy}: {str(e)}")
            continue
    
    return False

if __name__ == "__main__":
    url = "https://old.reddit.com/r/wallstreetbets/comments/1huwh0z/daily_discussion_thread_for_january_06_2025/"
    success = get_thread_content(url)
    if not success:
        print("Failed to access thread with all proxies")
