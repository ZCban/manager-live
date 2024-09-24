import subprocess
import os
import threading

# Funzione per eseguire mitmproxy
def run_proxy():
    subprocess.run(["mitmproxy", "-s", "mock3.py"])

# Avvia mitmproxy in un thread separato
proxy_thread = threading.Thread(target=run_proxy)
proxy_thread.start()

# Imposta le variabili d'ambiente per il proxy
env = os.environ.copy()
env['HTTP_PROXY'] = 'http://localhost:8080'
env['HTTPS_PROXY'] = 'http://localhost:8080'

# Percorso al binario di DVDFab
#dvdfab_path = r"C:\Users\Admin\Desktop\streamfab_6.1.9.8\StreamFab\StreamFabPortable.exe"
dvdfab_path = r"C:\Program Files\StreamFab\StreamFab\StreamFab64.exe"
# Avvia DVDFab con il proxy
subprocess.run([dvdfab_path], env=env)
