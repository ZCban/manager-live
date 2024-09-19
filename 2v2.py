import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, parse_qs
import tkinter as tk
from tkinter import ttk
import webbrowser
import os
from datetime import datetime

# List of pages to analyze
urls_to_analyze = [
    'https://home.sportsurge.club/',
    'https://sporttuna.sx/live/football/',
    'https://calciostreaming.ink/',
    'https://calciostreaming.guru',
    'https://hattrick.ws/live77.htm',
    'https://calcio.my/streaming-gratis-calcio-1.php',
    'https://enigma4k.live/',
    'https://it.vipleague.im/football-schedule-streaming-links',
    'https://sportzone.my/',
    'https://calcioinstreaming.online/',
]

# Excluded patterns (domains or specific parts of URLs)
EXCLUDED_PATTERNS = [
    'www.liveinternet.ru',
    'calcio01.live',
    'rbtv77live2',  # This pattern blocks URLs containing 'rbtv77live2' in the domain or path
    'icon_filter_livess_active.svg',
    'icon_switch_live@2x.webp',
    'soccerlive.app'
]

# Log directory
LOG_DIR = 'log'

# Ensure log directory exists
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

# Add a User-Agent to simulate a browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) \
Chrome/98.0.4758.102 Safari/537.36'
}

# Function to check if a domain or path is excluded
def is_domain_excluded(url):
    parsed_url = urlparse(url)
    for pattern in EXCLUDED_PATTERNS:
        if pattern in parsed_url.netloc or pattern in parsed_url.path:
            return True
    return False

# Function to log errors
def log_error(message):
    error_filename = os.path.join(LOG_DIR, 'error_log.txt')
    with open(error_filename, 'a', encoding='utf-8') as error_file:
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        error_file.write(f"{timestamp} - {message}\n")

# Function to analyze a single page and return URLs containing 'live'
def analyze_page(url):
    try:
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            live_urls = set()

            for tag in soup.find_all(['a', 'img', 'script', 'link', 'iframe', 'source', 'video', 'audio']):
                for attribute in ['href', 'src', 'data-src']:
                    url_candidate = tag.get(attribute)
                    if url_candidate:
                        full_url = urljoin(url, url_candidate)
                        if 'live' in full_url and not is_domain_excluded(full_url):
                            live_urls.add(full_url)

            return live_urls
        else:
            log_error(f"Request failed with status code {response.status_code} for URL: {url}")
            return set()
    except Exception as e:
        log_error(f"Error analyzing page {url}: {e}")
        return set()

# Function to get the live name from URL
def get_live_name(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    if 'ch' in query_params:
        return query_params['ch'][0]
    else:
        path_parts = [part for part in parsed_url.path.split('/') if part]
        return path_parts[-1] if path_parts else 'Unknown'

# Function to create a log file for URLs
def create_url_log_file(urls_by_domain):
    log_filename = os.path.join(LOG_DIR, f"log_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt")
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        for domain, urls in urls_by_domain.items():
            log_file.write(f"Domain: {domain}\n")
            for url in urls:
                log_file.write(f"  {url}\n")
            log_file.write("\n")
    print(f"URL log file created: {log_filename}")

# Function to open the link in the browser
def open_link(url):
    webbrowser.open(url)

# Function to create the GUI
def create_gui(live_urls):
    root = tk.Tk()
    root.title("Live URL Finder")
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True)

    label = ttk.Label(main_frame, text="Found URLs containing 'live':", font=("Arial", 14))
    label.grid(row=0, column=0, columnspan=5, pady=10)

    urls_by_domain = {}
    for url in live_urls:
        domain = urlparse(url).netloc
        if domain not in urls_by_domain and not is_domain_excluded(url):
            urls_by_domain[domain] = []
        urls_by_domain[domain].append(url)

    create_url_log_file(urls_by_domain)

    column = 0
    for domain, urls in urls_by_domain.items():
        domain_frame = ttk.LabelFrame(main_frame, text=domain)
        domain_frame.grid(row=1, column=column, padx=10, pady=10, sticky='n')
        for url in urls:
            live_name = get_live_name(url)
            button = ttk.Button(domain_frame, text=live_name, command=lambda u=url: open_link(u))
            button.pack(pady=5, fill='x')
        column += 1

    root.mainloop()

# Analyze all pages and collect 'live' URLs
all_live_urls = set()
for url in urls_to_analyze:
    live_urls_from_page = analyze_page(url)
    all_live_urls.update(live_urls_from_page)

# Start the GUI with the collected URLs
create_gui(all_live_urls)
