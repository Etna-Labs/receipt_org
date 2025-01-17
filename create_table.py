import pandas as pd
from tabulate import tabulate
import json
from collections import defaultdict

def create_results_table():
    """
    Create a comprehensive results table combining mention counts, sentiment analysis,
    and trading context while maintaining the original column structure.
    """
    # Read mention counts from company_mention_counter.py output
    from company_mention_counter import combine_company_ticker
    with open('wsb_thread.txt', 'r', encoding='utf-8') as f:
        content = f.read()
    mention_counts = combine_company_ticker(content)
    
    # Get sentiment data from analyzer
    from sentiment_analyzer import analyze_sentiment_for_companies
    sentiment_results = analyze_sentiment_for_companies()
    
    # Create DataFrame with sentiment analysis results
    data = defaultdict(lambda: {
        'mentions': 0,
        'sentiment': 'Neutral',
        'sentiment_score': 0.0,
        'key_context': 'Limited meaningful discussion'
    })
    
    # Process results for each ticker
    for ticker in set(list(mention_counts.keys()) + [r['ticker'] for r in sentiment_results]):
        # Update mentions count
        data[ticker]['mentions'] = mention_counts.get(ticker, 0)
        
        # Find sentiment result for this ticker
        sentiment_info = next((r for r in sentiment_results if r['ticker'] == ticker), None)
        if sentiment_info:
            # Update sentiment data
            data[ticker].update({
                'sentiment': sentiment_info['sentiment'],
                'sentiment_score': sentiment_info['score']
            })
            
            # Process trading contexts
            if sentiment_info.get('contexts'):
                contexts = sentiment_info['contexts']
                
                # Aggregate trading details
                price_targets = []
                position_types = []
                strategies = []
                risk_levels = []
                
                for context in contexts:
                    if context['price_targets']:
                        price_targets.extend(context['price_targets'])
                    if context['position_type']:
                        position_types.append(context['position_type'])
                    if context['strategy']:
                        strategies.append(context['strategy'])
                    if context['risk_level']:
                        risk_levels.append(context['risk_level'])
                
                # Create detailed context string
                context_parts = []
                if price_targets:
                    # Remove duplicates and sort price targets
                    unique_targets = sorted(set(price_targets), key=float)
                    context_parts.append(f"Price targets: ${', $'.join(unique_targets)}")
                if position_types:
                    most_common_position = max(set(position_types), key=position_types.count)
                    context_parts.append(f"Position: {most_common_position}")
                if strategies:
                    most_common_strategy = max(set(strategies), key=strategies.count)
                    context_parts.append(f"Strategy: {most_common_strategy}")
                if risk_levels:
                    most_common_risk = max(set(risk_levels), key=risk_levels.count)
                    context_parts.append(f"Risk: {most_common_risk}")
                
                if context_parts:
                    data[ticker]['key_context'] = ' | '.join(context_parts)
            
    # Create DataFrame and sort by mentions
    df = pd.DataFrame.from_dict(data, orient='index')
    df = df.sort_values('mentions', ascending=False)
    
    # Generate key observations
    key_observations = []
    
    # Most discussed stocks
    top_discussed = df.head(3).index.tolist()
    key_observations.append(f"Most discussed: {', '.join(top_discussed)}")
    
    # Most bullish stocks
    bullish_stocks = df[df['sentiment'].isin(['Very Bullish', 'Bullish'])].sort_values('sentiment_score', ascending=False)
    if not bullish_stocks.empty:
        top_bullish = bullish_stocks.head(3).index.tolist()
        key_observations.append(f"Most bullish: {', '.join(top_bullish)}")
    
    # Most bearish stocks
    bearish_stocks = df[df['sentiment'].isin(['Very Bearish', 'Bearish'])].sort_values('sentiment_score')
    if not bearish_stocks.empty:
        top_bearish = bearish_stocks.head(3).index.tolist()
        key_observations.append(f"Most bearish: {', '.join(top_bearish)}")
    
    # Format the table
    formatted_table = tabulate(df.reset_index().values.tolist(),
                             headers=['Company/Ticker', 'Mentions', 'Sentiment', 'Score', 'Key Context'],
                             tablefmt='pipe', floatfmt='.2f')
    
    # Combine table with observations
    final_output = "Key Observations:\n"
    final_output += "\n".join(f"- {obs}" for obs in key_observations)
    final_output += "\n\n" + formatted_table
    
    # Save to file
    with open('wsb_analysis_results.txt', 'w') as f:
        f.write(final_output)
    
    return final_output
    
    # Create DataFrame
    df = pd.DataFrame.from_dict(data, orient='index')
    
    # Reorder columns
    df = df[['mentions', 'sentiment', 'sentiment_score', 'key_context']]
    
    # Sort by mentions
    df = df.sort_values('mentions', ascending=False)
    
    # Format the table
    formatted_table = tabulate(df.reset_index().values.tolist(),
                             headers=['Company/Ticker', 'Mentions', 'Sentiment', 'Score', 'Key Context'],
                             tablefmt='pipe', floatfmt='.2f')
    
    # Save to file
    with open('wsb_analysis_results.txt', 'w') as f:
        f.write(formatted_table)
    
    return formatted_table

if __name__ == "__main__":
    print("\nWallStreetBets Daily Discussion Analysis Results:")
    print("-" * 50)
    print(create_results_table())
