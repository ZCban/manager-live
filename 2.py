import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin, urlparse, parse_qs
import tkinter as tk
from tkinter import ttk
import webbrowser
import os
from datetime import datetime

# Lista delle pagine da analizzare
urls_to_analyze = [
    'https://calciostreaming.guru',
    'https://calcio.my/streaming-gratis-calcio-1.php',
    
    'https://sportzone.my/',
    'https://calcioinstreaming.online/',
]

# Aggiungi un User-Agent per simulare un browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
     Chrome/98.0.4758.102 Safari/537.36'
}

# Funzione per analizzare una singola pagina e restituire gli URL che contengono 'live'
def analyze_page(url):
    try:
        response = requests.get(url, headers=headers)

        # Controllare che la richiesta sia andata a buon fine
        if response.status_code == 200:
            # Parsing del contenuto HTML
            soup = BeautifulSoup(response.text, 'html.parser')

            # Inizializzare un set per raccogliere tutti gli URL unici
            live_urls = set()

            # Trova tutti i tag con attributi che possono contenere URL
            for tag in soup.find_all(['a', 'img', 'script', 'link', 'iframe', 'source', 'video', 'audio']):
                for attribute in ['href', 'src', 'data-src']:
                    url_candidate = tag.get(attribute)
                    if url_candidate:
                        full_url = urljoin(url, url_candidate)
                        # Filtra solo gli URL che contengono la parola "live"
                        if 'live' in full_url:
                            live_urls.add(full_url)

            # Cerca URL all'interno di attributi di stile (background images, ecc.)
            for tag in soup.find_all(style=True):
                style = tag['style']
                urls_in_style = re.findall(r'url\((.*?)\)', style)
                for u in urls_in_style:
                    u = u.strip('\'"')
                    full_url = urljoin(url, u)
                    # Filtra solo gli URL che contengono la parola "live"
                    if 'live' in full_url:
                        live_urls.add(full_url)

            # Cerca URL e token all'interno di script o testo
            scripts = soup.find_all('script')
            for script in scripts:
                script_content = script.string or ''
                # Ricerca di URL
                urls_in_script = re.findall(r'(https?://\S+)', script_content)
                for u in urls_in_script:
                    u = u.strip('\'",;')
                    # Filtra solo gli URL che contengono la parola "live"
                    if 'live' in u:
                        live_urls.add(u)

            return live_urls
        else:
            print(f"Errore durante la richiesta: {response.status_code}")
            return set()

    except Exception as e:
        print(f"Errore durante l'analisi della pagina {url}: {e}")
        return set()

# Funzione per estrarre il nome della live dall'URL
def get_live_name(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    
    # Se l'URL contiene il parametro "ch", usa il suo valore come nome della live
    if 'ch' in query_params:
        return query_params['ch'][0]
    # Se no, usa l'ultima parte del percorso dell'URL
    else:
        path_parts = parsed_url.path.split('/')
        return path_parts[-1] if path_parts[-1] else path_parts[-2]

# Funzione per estrarre il dominio dall'URL
def get_domain(url):
    parsed_url = urlparse(url)
    return parsed_url.netloc

# Funzione per creare un file di log
def create_log_file(urls_by_domain):
    # Crea o aggiorna il file di log
    log_filename = f"log_urls_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    
    with open(log_filename, 'w', encoding='utf-8') as log_file:
        for domain, urls in urls_by_domain.items():
            log_file.write(f"Domain: {domain}\n")
            for url in urls:
                log_file.write(f"  {url}\n")
            log_file.write("\n")
    
    print(f"Log file creato: {log_filename}")

# Analizzare tutte le pagine e raccogliere gli URL 'live'
all_live_urls = set()

for url in urls_to_analyze:
    live_urls_from_page = analyze_page(url)
    all_live_urls.update(live_urls_from_page)

# Funzione per aprire il link nel browser
def open_link(url):
    webbrowser.open(url)

# Funzione per creare la GUI e suddividere i tasti in base al dominio, organizzati in colonne
def create_gui(live_urls):
    root = tk.Tk()
    root.title("Live URL Finder")

    # Creare un Frame per il layout principale
    main_frame = ttk.Frame(root)
    main_frame.pack(fill='both', expand=True)

    # Etichetta principale
    label = ttk.Label(main_frame, text="Found URLs containing 'live':", font=("Arial", 14))
    label.grid(row=0, column=0, columnspan=5, pady=10)

    # Raggruppare gli URL in base al dominio
    urls_by_domain = {}
    for url in live_urls:
        domain = get_domain(url)
        if domain not in urls_by_domain:
            urls_by_domain[domain] = []
        urls_by_domain[domain].append(url)

    # Creare il file di log con gli URL trovati
    create_log_file(urls_by_domain)

    # Creare sezioni separate per ogni dominio, distribuite su colonne
    column = 0
    for domain, urls in urls_by_domain.items():
        # Creare un Frame per il dominio
        domain_frame = ttk.LabelFrame(main_frame, text=domain)
        domain_frame.grid(row=1, column=column, padx=10, pady=10, sticky='n')

        # Creare i bottoni per ciascun URL del dominio
        for url in urls:
            live_name = get_live_name(url)
            button = ttk.Button(domain_frame, text=live_name, command=lambda u=url: open_link(u))
            button.pack(pady=5, fill='x')

        # Passa alla colonna successiva
        column += 1

    root.mainloop()

# Avvia l'interfaccia grafica con gli URL trovati
create_gui(all_live_urls)
