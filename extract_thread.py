from bs4 import BeautifulSoup
import re

def clean_username(username):
    # Remove common prefixes and clean up username
    if username.startswith('/u/'):
        username = username[3:]
    return username.strip()

def extract_comments(html_content):
    # Parse HTML content
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all comment blocks
    comments = []
    
    # Look for comments in the pre-formatted content
    pre_content = soup.find('pre')
    if not pre_content:
        print("No pre content found")
        return "No content found"
        
    content_text = pre_content.get_text()
    print(f"Found pre-formatted content of length: {len(content_text)}")
    
    # Find the start of the actual content
    content_lines = content_text.split('\n')
    print(f"Total number of lines: {len(content_lines)}")
    
    # Filter out navigation and UI elements
    filtered_lines = []
    in_comments_section = False
    skip_patterns = [
        'permalink', 'embed', 'save', 'report', 'reply', 'parent',
        'children', 'points', 'submitted', 'ago', 'http', 'html',
        'subreddit', 'jump to content', 'my subreddits', '===============',
        'javascript:', 'about', 'help', 'apps & tools', '<3', 'REDDIT',
        'sorted by:', 'share', 'hide', '[load more', 'MODERATORS',
        'markdown content:', 'title:', 'url source:', '|', 'limit my search',
        'author:', 'find submissions', 'search for', 'self:', 'nsfw:',
        'shortlink:', 'the rules', '* * *', '**', 'navigate wsb',
        'a community for', '==========', 'sorted by:', '\[deleted\]'
    ]
    
    def clean_text(text):
        # Remove emoji codes
        text = re.sub(r':\d+:', '', text)
        # Remove other emoji codes
        text = re.sub(r':[a-zA-Z0-9_]+:', '', text)
        # Clean up whitespace
        text = ' '.join(text.split())
        return text
    
    for line in content_lines:
        line = line.strip()
        
        # Skip empty lines and lines with UI elements
        if not line or any(x in line.lower() for x in skip_patterns):
            continue
            
        # Check if we've reached the comments section
        if ("What Are Your Moves Tomorrow" in line or 
            "Daily Discussion Thread" in line) and "january" in line.lower():
            in_comments_section = True
            print(f"Found thread title: {line.strip()}")
            filtered_lines.append(line)
            continue
            
        # Only include lines after we've found the title
        if in_comments_section:
            # Skip lines that are just numbers or single characters
            if line.isdigit() or len(line) <= 1:
                continue
            # Skip lines that are just emoji codes
            if line.startswith(':') and line.endswith(':'):
                continue
            filtered_lines.append(line)
    
    if not filtered_lines:
        print("Could not find any valid content")
        return "No content found"
        
    print(f"Found {len(filtered_lines)} filtered lines")
    print("Sample of filtered content:")
    for line in filtered_lines[:10]:
        print(f"- {line}")
    
    current_user = None
    current_comment = []
    in_comment = False
    comments_found = 0
    
    for line in content_lines:
        line = line.strip()
        
        # Skip empty lines and navigation elements
        if not line or any(x in line.lower() for x in [
            'permalink', 'embed', 'save', 'report', 'reply', 'parent',
            'children', 'points', 'submitted', 'ago', 'http', 'html',
            'subreddit', 'jump to content', 'my subreddits', '==============='
        ]):
            continue
            
        # Debug output for non-skipped lines
        if len(line.strip()) > 0:
            print(f"Processing line: {line[:100]}")
            
        # Each non-empty line that's not a title or navigation element is treated as a comment
        if len(line.strip()) > 0 and not any(x in line.lower() for x in [
            'what are your moves tomorrow', 'daily discussion thread'
        ]):
            # Skip lines that are just formatting or navigation
            if (line.startswith('*') or line.startswith('[') or 
                line.startswith('=') or line.startswith('<') or
                line.startswith('>') or line.isdigit() or
                len(line.strip()) <= 2):  # Skip very short lines
                continue
                
            # Clean and validate the comment
            cleaned_comment = clean_text(line.strip())
            if len(cleaned_comment) > 5:  # Only keep meaningful comments
                comments.append(("anonymous", cleaned_comment))
                print(f"Found comment: {cleaned_comment[:100]}")
        
        # Add line to current comment if we're in a comment
        elif in_comment and current_user:
            if (not line.startswith('*') and 
                not line.startswith('[') and 
                not line.startswith('=') and
                len(line) > 0):
                current_comment.append(line)
                    
    # Continue processing comments
    
    # Save last comment if exists
    if current_user and current_comment:
        comment_text = ' '.join(current_comment).strip()
        if len(comment_text) > 20:
            comments.append((current_user, comment_text))
    
    print(f"\nExtraction Summary:")
    print(f"Total comments found: {len(comments)}")
    if comments:
        print("Sample comments:")
        for i, (user, comment) in enumerate(comments[:3]):
            print(f"{i+1}. {user}: {comment[:100]}...")
    
    # Find the title from the pre-formatted content
    title_text = "No title found"
    for line in content_lines:
        if "What Are Your Moves Tomorrow" in line and not any(x in line.lower() for x in ['http', 'html', '<', 'markdown']):
            title_text = line.strip()
            print(f"Found title: {title_text}")
            break
    
    # Remove duplicate comments and prepare final text
    seen_comments = set()
    unique_comments = []
    for username, comment in comments:
        if comment not in seen_comments:
            seen_comments.add(comment)
            unique_comments.append((username, comment))
    
    # Prepare the final text with title and numbered comments
    full_text = f"Thread Title: {title_text}\n\n"
    for i, (username, comment) in enumerate(unique_comments, 1):
        if len(comment.strip()) > 0:  # Skip empty comments
            full_text += f"Comment {i}:\n{comment}\n---\n"
    
    # Save the extracted content to files
    
    # Save both raw HTML and extracted text
    with open('wsb_thread.html', 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    with open('wsb_thread.txt', 'w', encoding='utf-8') as f:
        f.write(full_text)
    
    return full_text

if __name__ == "__main__":
    # Read the HTML file from the latest browser output
    with open('/home/ubuntu/full_outputs/page_html_1737102318.7306762.txt', 'r', encoding='utf-8') as f:
        html_content = f.read()
    
    # Extract and save comments
    extracted_text = extract_comments(html_content)
    print("Thread content extracted and saved to wsb_thread.txt")
    print("Raw HTML saved to wsb_thread.html")
    
    # Print first few lines of extracted content for verification
    print("\nFirst few lines of extracted content:")
    print("\n".join(extracted_text.split("\n")[:5]))
