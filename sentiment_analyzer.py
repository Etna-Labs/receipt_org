from textblob import TextBlob
import re
from collections import defaultdict
import re  # Ensure re is imported for regex operations

def get_user_reputation(comment_text):
    """
    Calculate user reputation based on comment quality indicators.
    Returns a multiplier between 1.0 and 1.5
    """
    reputation_score = 1.0
    
    # Check for high-quality indicators
    quality_indicators = {
        'technical_analysis': ['RSI', 'MACD', 'moving average', 'support', 'resistance', 'volume'],
        'fundamental_analysis': ['earnings', 'revenue', 'growth', 'market share', 'guidance'],
        'detailed_reasoning': ['because', 'due to', 'based on', 'analysis shows'],
        'position_disclosure': ['position:', 'holding:', 'bought', 'sold']
    }
    
    # Calculate score based on indicators
    for category, indicators in quality_indicators.items():
        if any(indicator.lower() in comment_text.lower() for indicator in indicators):
            reputation_score += 0.1  # Max 0.4 from all categories
            
    # Check for length and structure
    words = comment_text.split()
    if len(words) > 100:  # Longer, more detailed comments
        reputation_score += 0.1
        
    # Cap at 1.5
    return min(1.5, reputation_score)

def extract_trading_details(text):
    """
    Extract specific trading details from comment text.
    Returns a dictionary of extracted details.
    """
    details = {
        'price_targets': [],
        'position_type': None,
        'strategy': None,
        'risk_level': None
    }
    
    # Extract price targets (e.g., "$450", "450$", "450 dollars")
    price_pattern = r'\$?\d+\.?\d*\$?|\$?\d+\.?\d*\s?(?:dollars?|USD)'
    prices = re.findall(price_pattern, text)
    if prices:
        details['price_targets'] = [p.strip('$ ') for p in prices]
    
    # Identify position type
    long_indicators = ['calls', 'long', 'buy', 'buying', 'bullish', 'moon']
    short_indicators = ['puts', 'short', 'sell', 'selling', 'bearish', 'dump']
    
    text_lower = text.lower()
    if any(indicator in text_lower for indicator in long_indicators):
        details['position_type'] = 'Long'
    elif any(indicator in text_lower for indicator in short_indicators):
        details['position_type'] = 'Short'
    
    # Identify trading strategy
    strategies = {
        'swing': ['swing', 'weekly', 'monthly'],
        'day': ['day trade', 'scalp', 'intraday'],
        'options': ['call', 'put', 'strike', 'expiry'],
        'value': ['undervalued', 'oversold', 'fundamental'],
        'momentum': ['trend', 'breakout', 'momentum']
    }
    
    for strategy, keywords in strategies.items():
        if any(keyword in text_lower for keyword in keywords):
            details['strategy'] = strategy.title()
            break
    
    # Assess risk level
    risk_indicators = {
        'High': ['yolo', 'all in', 'lottery', '0dte', 'fd'],
        'Medium': ['risky', 'volatile', 'leverage'],
        'Low': ['safe', 'conservative', 'hedge', 'small position']
    }
    
    for risk_level, indicators in risk_indicators.items():
        if any(indicator in text_lower for indicator in indicators):
            details['risk_level'] = risk_level
            break
    
    return details

def analyze_sentiment_for_companies():
    # Read the thread content
    with open('wsb_thread.txt', 'r', encoding='utf-8') as f:
        content = f.read()

    # Split into comments more accurately
    comments = []
    current_comment = []
    
    for line in content.split('\n'):
        if line.startswith('Comment '):
            if current_comment:
                comments.append(' '.join(current_comment))
            current_comment = []
        elif line.strip() and not line.startswith('Thread Title:') and not line.startswith('---'):
            current_comment.append(line.strip())
    
    if current_comment:
        comments.append(' '.join(current_comment))

    # Company ticker mapping
    companies = {
        'NVDA': ['NVDA', 'NVIDIA'],
        'TSLA': ['TSLA', 'TESLA'],
        'CVNA': ['CVNA', 'CARVANA'],
        'SPY': ['SPY'],
        'TLT': ['TLT'],
        'FUBO': ['FUBO'],
        'URA': ['URA'],
        'AMZN': ['AMZN', 'AMAZON'],
        'AAPL': ['AAPL', 'APPLE'],
        'PLTR': ['PLTR', 'PALANTIR'],
        'MSTR': ['MSTR', 'MICROSTRATEGY'],
        'AMD': ['AMD', 'ADVANCED MICRO DEVICES'],
        'GOOGL': ['GOOGL', 'GOOGLE', 'ALPHABET'],
        'META': ['META', 'FACEBOOK'],
        'MSFT': ['MSFT', 'MICROSOFT'],
        'DDOG': ['DDOG', 'DATADOG'],
        'IWM': ['IWM', 'RUSSELL 2000'],
        'KULR': ['KULR'],
        'RGTI': ['RGTI', 'RIGETTI']
    }

    # Store sentiment scores and contexts
    sentiment_data = defaultdict(lambda: {'scores': [], 'contexts': []})

    # Analyze each comment
    for comment in comments:
        if not comment.strip():
            continue

        # Split comment into sentences for better context
        sentences = TextBlob(comment).sentences
        
        # Check for company mentions and analyze local context
        for ticker, names in companies.items():
            for name in names:
                for i, sentence in enumerate(sentences):
                    if re.search(r'\b' + name + r'\b', sentence.raw.upper()):
                        # Get local context (previous and next sentence if available)
                        start_idx = max(0, i-1)
                        end_idx = min(len(sentences), i+2)
                        context_sentences = sentences[start_idx:end_idx]
                        
                        # Calculate weighted sentiment based on local context
                        context_text = ' '.join(str(s) for s in context_sentences)
                        context_blob = TextBlob(context_text)
                        
                        # Weight sentiment more heavily if company is mentioned with sentiment words
                        sentiment_words = ['bullish', 'bearish', 'calls', 'puts', 'moon', 'dump', 'pump', 'crash']
                        sentiment_multiplier = 1.5 if any(word in context_text.lower() for word in sentiment_words) else 1.0
                        
                        # Apply user reputation multiplier
                        user_reputation = get_user_reputation(context_text)
                        sentiment_score = context_blob.sentiment.polarity * sentiment_multiplier * user_reputation
                        sentiment_data[ticker]['scores'].append(sentiment_score)
                        
                        # Extract trading details
                        trading_details = extract_trading_details(context_text)
                        
                        # Store context and trading details if there's any notable sentiment
                        if abs(sentiment_score) > 0.1:
                            context_entry = {
                                'text': context_text,
                                'price_targets': trading_details['price_targets'],
                                'position_type': trading_details['position_type'],
                                'strategy': trading_details['strategy'],
                                'risk_level': trading_details['risk_level']
                            }
                            sentiment_data[ticker]['contexts'].append(context_entry)

    # Calculate average sentiment and prepare results
    results = []
    for ticker, data in sentiment_data.items():
        if data['scores']:
            avg_sentiment = sum(data['scores']) / len(data['scores'])
            
            # More nuanced sentiment labels with lower thresholds
            if avg_sentiment > 0.2:
                sentiment_label = 'Very Bullish'
            elif avg_sentiment > 0.05:
                sentiment_label = 'Bullish'
            elif avg_sentiment < -0.2:
                sentiment_label = 'Very Bearish'
            elif avg_sentiment < -0.05:
                sentiment_label = 'Bearish'
            else:
                sentiment_label = 'Neutral'
            
            # Sort contexts by absolute sentiment strength
            sorted_contexts = sorted(data['contexts'], key=lambda x: abs(TextBlob(x['text']).sentiment.polarity), reverse=True)
            
            results.append({
                'ticker': ticker,
                'sentiment': sentiment_label,
                'score': avg_sentiment,
                'mention_count': len(data['scores']),
                'contexts': sorted_contexts[:3]  # Include up to 3 strongest sentiment contexts with trading details
            })

    # Sort by absolute sentiment strength
    results.sort(key=lambda x: abs(x['score']), reverse=True)
    
    return results

if __name__ == "__main__":
    # Print results in a formatted way when run directly
    results = analyze_sentiment_for_companies()
    print("\nSentiment Analysis Results:")
    print("-" * 50)
    for result in results:
        print(f"\n{result['ticker']} - {result['sentiment']}")
        print(f"Sentiment Score: {result['score']:.2f}")
        print(f"Mention Count: {result['mention_count']}")
        if result['contexts']:
            print("Example contexts:")
            for ctx in result['contexts']:
                print(f"- Text: {ctx['text'][:100]}...")
                if ctx['price_targets']:
                    print(f"  Price targets: ${', $'.join(ctx['price_targets'])}")
                if ctx['position_type']:
                    print(f"  Position: {ctx['position_type']}")
                if ctx['strategy']:
                    print(f"  Strategy: {ctx['strategy']}")
                if ctx['risk_level']:
                    print(f"  Risk: {ctx['risk_level']}")
