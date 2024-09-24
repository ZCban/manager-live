import subprocess
import os
import threading
import time
import subprocess
import sys
import os

def kill_process_on_port(port):
    """ Kills processes running on the given port. """
    if os.name == 'nt':  # For Windows
        command = f'netstat -ano | findstr :{port}'
        try:
            lines = subprocess.check_output(command, shell=True).decode().strip().split('\n')
            for line in lines:
                parts = line.strip().split()
                if len(parts) > 4 and parts[3].endswith(str(port)):
                    pid = parts[-1]  # Get the PID from the output
                    print(f"Killing PID {pid} on port {port}")
                    subprocess.run(['taskkill', '/PID', pid, '/F'])
        except subprocess.CalledProcessError as e:
            print(f"No processes found on port {port}.")
    else:  # For Unix-like systems (Linux/macOS)
        command = f"lsof -i :{port} | awk '{{print $2}}' | grep -v PID"
        try:
            pid = subprocess.check_output(command, shell=True).decode().strip()
            if pid:
                print(f"Killing PID {pid} on port {port}")
                subprocess.run(['kill', '-9', pid])
        except subprocess.CalledProcessError as e:
            print(f"No processes found on port {port}.")


# Funzione per eseguire mitmproxy in un nuovo cmd con log di output e errori
def run_proxy():
    with open("mitmproxy_output.log", "w") as out, open("mitmproxy_error.log", "w") as err:
        cmd_command = "mitmproxy -s mock3.py --set connection_strategy=eager --listen-port 8080"#--set connection_strategy=eager
        try:
            # Avvia un nuovo terminale cmd che esegue mitmproxy e redirige l'output
            subprocess.run(["start", "cmd", "/k", f"echo {cmd_command} && {cmd_command}"],
                           stdout=out, stderr=err, text=True, shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Errore durante l'esecuzione di mitmproxy: {e}")


def import_certificates(cert_directory):
    for cert_file in os.listdir(cert_directory):
        if cert_file.endswith('.crt'):
            full_path = os.path.join(cert_directory, cert_file)
            print(f"Importing {full_path}...")

            import_command = [
                "certutil", "-addstore", "-f", "root", full_path
            ]
            
            try:
                result = subprocess.run(import_command, capture_output=True, text=True, check=True)
                print(result.stdout)
            except subprocess.CalledProcessError as e:
                print("Error during certificate import:")
                print(e.output)

ports = [8082, 8080]
for port in ports:
    kill_process_on_port(port)
# Importa tutti i certificati dalla cartella specificata
cert_folder_path = "cert"
import_certificates(cert_folder_path)

# Avvia mitmproxy in un thread separato
proxy_thread = threading.Thread(target=run_proxy)
proxy_thread.start()

time.sleep(2)

env = os.environ.copy()
env['HTTP_PROXY'] = 'http://localhost:8080'
env['HTTPS_PROXY'] = 'http://localhost:8080'

# Percorso al binario di DVDFab
dvdfab_path = r"C:\Program Files\StreamFab\StreamFab\StreamFab64.exe"
#dvdfab_path = r"C:\Users\Admin\Desktop\streamfab_6.1.9.8\StreamFab\StreamFabPortable.exe"

# Avvia DVDFab con il proxy e salva output/errori in file di log
with open("dvdfab_output.log", "w") as dvdfab_out, open("dvdfab_error.log", "w") as dvdfab_err:
    try:
        process = subprocess.run([dvdfab_path], env=env, stdout=dvdfab_out, stderr=dvdfab_err, timeout=1200)
    except subprocess.TimeoutExpired:
        dvdfab_err.write("DVDFab ha raggiunto il timeout ed è stato terminato.\n")

# Assicurarsi che mitmproxy termini correttamente
#proxy_thread.join()
