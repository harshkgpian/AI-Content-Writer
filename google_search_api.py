import requests
from bs4 import BeautifulSoup
import numpy as np
import re
from groq_api import summarize, generate_keywords, generate_web_search_queries, specifications, write_blog_post, edit_and_proofread, ask_follow_up_question 
# Groq API functions should be defined here
# from groq_api import summarize, generate_keywords, generate_web_search_queries, specifications, write_blog_post 

# Set up your API key and Custom Search Engine ID
API_KEY = 'YOUR_API_KEY'
CSE_ID = 'YOUR_CSE_ID'

# Initialize a global token counter
total_tokens = 0
MAX_TOKENS = 50000  # Maximum tokens allowed

# Function to get search results from Google Custom Search API
def google_search(query, api_key, cse_id, num_results=3):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={api_key}&cx={cse_id}&num={num_results}"
    response = requests.get(search_url)
    results = response.json()
    return results.get('items', [])

# Function to scrape targeted content from a webpage with a timeout and error handling
def scrape_content(url, timeout=30):
    try:
        response = requests.get(url, timeout=timeout)
        response.raise_for_status()  # Raise an error for HTTP errors (e.g., 404, 500)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract main content from articles
        paragraphs = []
        for tag in soup.find_all(['article', 'main']):
            paragraphs.extend(tag.find_all('p'))

        if not paragraphs:
            # Fallback to extracting paragraphs if no article/main tags found
            paragraphs = soup.find_all('p')

        content = ' '.join([para.get_text() for para in paragraphs])
        return content
    except requests.Timeout:
        print(f"Scraping timed out for URL: {url}")
        return ""
    except requests.RequestException as e:
        print(f"Scraping Error for URL: {url}: {e}")
        return ""

# Function to preprocess text
def preprocess_text(content):
    # Remove HTML tags
    content = re.sub(r'<[^>]+>', '', content)
    # Remove multiple newlines and excessive whitespace
    content = re.sub(r'\s+', ' ', content).strip()
    # Remove any irrelevant text patterns (e.g., disclaimers, ads, etc.)
    content = re.sub(r'Read more:.*|Subscribe to our newsletter.*|Follow us on.*', '', content, flags=re.IGNORECASE)
    return content

# Custom Count Vectorizer function
def custom_count_vectorizer(content, vocabulary):
    content = content.lower()
    token_counts = {word: 0 for word in vocabulary}
    
    for word in vocabulary:
        token_counts[word] = content.count(word.lower())
    
    return token_counts

# Function to determine relevance of a webpage's content
def determine_relevance(content, relevant_keywords):
    token_counts = custom_count_vectorizer(content, relevant_keywords)
    relevance_score = sum(token_counts.values())
    content_length = len(content)
    return relevance_score, content_length

# Function to split content into chunks with overlap
def split_content(content, chunk_size=1000, overlap=100):
    chunks = []
    for i in range(0, len(content), chunk_size - overlap):
        chunks.append(content[i:i + chunk_size])
    return chunks

# Function to call Groq API and track tokens
def groq_api_call(api_func, *args):
    global total_tokens
    result, tokens = api_func(*args)
    total_tokens += tokens
    return result

# Example usage
Topic = input("Enter the topic: ")
print(Topic.split())
# Generate search queries and extract queries
query_list = (groq_api_call(generate_web_search_queries, Topic))[:1]
print(query_list)

sites = 1
combined_summaries = []
scraped_urls = set()

for query in query_list:
    if total_tokens >= MAX_TOKENS:
        break

    relevant_keywords = list(set(Topic.split()+groq_api_call(generate_keywords, query)))
    print(relevant_keywords)

    search_results = google_search(query, API_KEY, CSE_ID)
    
    relevance_scores = []
    scraped_contents = []
    urls = []

    for result in search_results:
        if total_tokens >= MAX_TOKENS:
            break

        url = result['link']
        if url in scraped_urls:
            continue
        scraped_urls.add(url)
        print(f"Scraping URL: {url}")
        
        content = scrape_content(url)
        content = preprocess_text(content)
        relevance_score, content_length = determine_relevance(content, relevant_keywords)
        print(f"Relevance Score: {relevance_score}, Content Length: {content_length}")
        
        relevance_scores.append((relevance_score, content_length))
        scraped_contents.append(content)
        urls.append(url)

    # Select the top websites with the highest relevance scores
    top_indices = sorted(range(len(relevance_scores)), key=lambda i: relevance_scores[i][0], reverse=True)[:sites]

    for idx in top_indices:
        if total_tokens >= MAX_TOKENS:
            break

        best_content = scraped_contents[idx]
        best_url = urls[idx]
        
        print(f"Summarizing content from URL {best_url}")
        
        chunked_content = split_content(best_content, chunk_size=3000, overlap=200)
        for chunk in chunked_content:
            if total_tokens >= MAX_TOKENS:
                break
            chunk_summary = groq_api_call(summarize, chunk)
            print("Summary:", chunk_summary)
            combined_summaries.append(chunk_summary)

combined_summary = " ".join(combined_summaries)
words = 700

print("Summarization completed.")

if total_tokens < MAX_TOKENS:
    specification = groq_api_call(specifications, Topic, combined_summary)
    blog_post = groq_api_call(write_blog_post, Topic, combined_summary, specification, words)
    blog = groq_api_call(edit_and_proofread,Topic,blog_post)
    blog_post = groq_api_call(write_blog_post, Topic, blog, specification, words)

    print(f"Blog Post:\n{blog}")
    with open('blog.txt', 'w', encoding='utf-8') as file:
        file.write(blog_post)
    with open('blog_edited.txt', 'w', encoding='utf-8') as file:
        file.write(blog)
print(f"Total Tokens Used: {total_tokens}")
print(groq_api_call(ask_follow_up_question,Topic,blog_post))
# stop_words = {
#     'a', 'about', 'above', 'after', 'again', 'against', 'all', 'am', 'an', 'and', 'any', 'are', 'aren\'t', 'as', 'at', 'be', 'because', 'been', 
#     'before', 'being', 'below', 'between', 'both', 'but', 'by', 'can\'t', 'cannot', 'could', 'couldn\'t', 'did', 'didn\'t', 'do', 'does', 'doesn\'t', 
#     'doing', 'don\'t', 'down', 'during', 'each', 'few', 'for', 'from', 'further', 'had', 'hadn\'t', 'has', 'hasn\'t', 'have', 'haven\'t', 'having', 
#     'he', 'he\'d', 'he\'ll', 'he\'s', 'her', 'here', 'here\'s', 'hers', 'herself', 'him', 'himself', 'his', 'how', 'how\'s', 'i', 'i\'d', 'i\'ll', 
#     'i\'m', 'i\'ve', 'if', 'in', 'into', 'is', 'isn\'t', 'it', 'it\'s', 'its', 'itself', 'let\'s', 'me', 'more', 'most', 'mustn\'t', 'my', 'myself', 
#     'no', 'nor', 'not', 'of', 'off', 'on', 'once', 'only', 'or', 'other', 'ought', 'our', 'ours', 'ourselves', 'out', 'over', 'own', 'same', 'shan\'t', 
#     'she', 'she\'d', 'she\'ll', 'she\'s', 'should', 'shouldn\'t', 'so', 'some', 'such', 'than', 'that', 'that\'s', 'the', 'their', 'theirs', 'them', 
#     'themselves', 'then', 'there', 'there\'s', 'these', 'they', 'they\'d', 'they\'ll', 'they\'re', 'they\'ve', 'this', 'those', 'through', 'to', 'too', 
#     'under', 'until', 'up', 'very', 'was', 'wasn\'t', 'we', 'we\'d', 'we\'ll', 'we\'re', 'we\'ve', 'were', 'weren\'t', 'what', 'what\'s', 'when', 
#     'when\'s', 'where', 'where\'s', 'which', 'while', 'who', 'who\'s', 'whom', 'why', 'why\'s', 'with', 'won\'t', 'would', 'wouldn\'t', 'you', 'you\'d', 
#     'you\'ll', 'you\'re', 'you\'ve', 'your', 'yours', 'yourself', 'yourselves'
# }
# import time

# def preprocess(text):
#     # Function to remove HTML tags
#     clean_text = re.sub(r'<.*?>', '', text) 
#     # REmove stop words
#     words = clean_text.split()
#     filtered_words = [word for word in words if word.lower() not in stop_words]
#     return ' '.join(filtered_words)

# Topic = "IPL 2024"
# search_results = google_search(Topic, API_KEY, CSE_ID)

# keywords,tokens = generate_keywords(Topic)

# print(keywords)
# relevance = sorted([determine_relevance(preprocess(result['snippet'] + result['htmlSnippet']),keywords) for result in search_results])

# print(relevance)