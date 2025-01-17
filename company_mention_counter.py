import re
from collections import defaultdict

def combine_company_ticker(text):
    # Dictionary mapping company names to their tickers and vice versa
    company_mappings = {
        'NVIDIA': 'NVDA',
        'NVDA': 'NVDA',
        'Tesla': 'TSLA',
        'TSLA': 'TSLA',
        'Carvana': 'CVNA',
        'CVNA': 'CVNA',
        'SPY': 'SPY',
        'TLT': 'TLT',
        'FUBO': 'FUBO',
        'URA': 'URA',
        'Amazon': 'AMZN',
        'AMZN': 'AMZN',
        'Apple': 'AAPL',
        'AAPL': 'AAPL',
        'Palantir': 'PLTR',
        'PLTR': 'PLTR',
        'MicroStrategy': 'MSTR',
        'MSTR': 'MSTR',
        'AMD': 'AMD',
        'Advanced Micro Devices': 'AMD',
        'Google': 'GOOGL',
        'GOOGL': 'GOOGL',
        'Alphabet': 'GOOGL',
        'Meta': 'META',
        'META': 'META',
        'Facebook': 'META',
        'Microsoft': 'MSFT',
        'MSFT': 'MSFT',
        'DDOG': 'DDOG',
        'Datadog': 'DDOG',
        'IWM': 'IWM',
        'Russell 2000': 'IWM',
        'KULR': 'KULR',
        'Rigetti': 'RGTI',
        'RGTI': 'RGTI'
    }
    
    # Count mentions
    mentions = defaultdict(int)
    
    # Convert text to uppercase for consistent matching
    text_upper = text.upper()
    
    # Count ticker mentions
    for company, ticker in company_mappings.items():
        # Count uppercase ticker mentions
        ticker_count = len(re.findall(r'\b' + ticker.upper() + r'\b', text_upper))
        # Count company name mentions (case insensitive)
        company_count = len(re.findall(r'\b' + company.upper() + r'\b', text_upper))
        # Combine counts under the ticker
        mentions[ticker] += ticker_count + company_count
    
    return dict(mentions)

# Example usage:
if __name__ == "__main__":
    # Read the content from a file
    with open('wsb_thread.txt', 'r') as f:
        content = f.read()
    
    # Get mention counts
    mention_counts = combine_company_ticker(content)
    
    # Print results
    print("\nCompany/Ticker Mention Counts:")
    print("-" * 30)
    for ticker, count in sorted(mention_counts.items(), key=lambda x: x[1], reverse=True):
        if count > 0:  # Only show items with mentions
            print(f"{ticker}: {count} mentions")
