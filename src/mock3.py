import json
from mitmproxy import http

def load_rules():
    with open("HTTPToolkit_DVDFab.htkrules", "r") as f:
        return json.load(f)

rules = load_rules()

def request(flow: http.HTTPFlow):
    url = flow.request.pretty_url
    for item in rules['items']:
        if item['activated'] and flow.request.method == "POST":
            match_url = item['matchers'][0].get('regexSource', '')
            if match_url in url:
                # Esegue le azioni specificate dalle regole
                if item['handler']['type'] == 'simple':
                    data = bytes(item['handler']['data']['data'])
                    flow.response = http.Response.make(
                        item['handler']['status'], 
                        data, 
                        headers=item['handler']['headers']
                    )
                elif item['handler']['type'] == 'forward-to-host':
                    # Cambia l'host di destinazione
                    flow.request.host = item['handler']['forwarding']['targetHost']
                # Aggiungi altre condizioni come necessario

# Puoi eseguire questo script con mitmproxy utilizzando il seguente comando:
# mitmdump -s path_to_your_script.py

