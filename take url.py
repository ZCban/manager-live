import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# URL della pagina da analizzare
url = 'https://sportzone.my/'

# Aggiungi un User-Agent per simulare un browser
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)\
     Chrome/98.0.4758.102 Safari/537.36'
}

# Fare una richiesta GET alla pagina
response = requests.get(url, headers=headers)

# Controllare che la richiesta sia andata a buon fine
if response.status_code == 200:
    # Parsing del contenuto HTML
    soup = BeautifulSoup(response.text, 'html.parser')

    # Inizializzare un set per raccogliere tutti gli URL unici
    urls = set()
    tokens = set()

    # Trova tutti i tag con attributi che possono contenere URL
    for tag in soup.find_all(['a', 'img', 'script', 'link', 'iframe', 'source', 'video', 'audio']):
        for attribute in ['href', 'src', 'data-src']:
            url_candidate = tag.get(attribute)
            if url_candidate:
                full_url = urljoin(url, url_candidate)
                urls.add(full_url)

    # Cerca URL all'interno di attributi di stile (background images, ecc.)
    for tag in soup.find_all(style=True):
        style = tag['style']
        urls_in_style = re.findall(r'url\((.*?)\)', style)
        for u in urls_in_style:
            u = u.strip('\'"')
            full_url = urljoin(url, u)
            urls.add(full_url)

    # Cerca URL e token all'interno di script o testo
    scripts = soup.find_all('script')
    for script in scripts:
        script_content = script.string or ''
        # Ricerca di URL
        urls_in_script = re.findall(r'(https?://\S+)', script_content)
        for u in urls_in_script:
            u = u.strip('\'",;')
            urls.add(u)
        # Ricerca di token (pattern comune)
        potential_tokens = re.findall(r'["\'](token|access_token|api_key|apiKey)["\']:\s*["\'](\S+?)["\']', script_content)
        for token_name, token_value in potential_tokens:
            tokens.add(f"{token_name}: {token_value}")

    # Stampa tutti gli URL trovati
    for u in urls:
        print("URL:", u)
    # Stampa tutti i token trovati
    for t in tokens:
        print("Token:", t)

else:
    print(f"Errore durante la richiesta: {response.status_code}")

