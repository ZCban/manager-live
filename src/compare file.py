import os

def list_files_in_directory(directory):
    """
    Restituisce un insieme dei nomi dei file presenti nella directory specificata.
    """
    return set(os.listdir(directory))

def compare_directories(dir1, dir2):
    """
    Confronta i file presenti in due cartelle e restituisce i file che sono presenti
    in una cartella ma non nell'altra.
    """
    # Otteniamo l'insieme dei file nelle due cartelle
    files_in_dir1 = list_files_in_directory(dir1)
    files_in_dir2 = list_files_in_directory(dir2)

    # Troviamo i file presenti in dir1 ma non in dir2
    only_in_dir1 = files_in_dir1 - files_in_dir2

    # Troviamo i file presenti in dir2 ma non in dir1
    only_in_dir2 = files_in_dir2 - files_in_dir1

    return only_in_dir1, only_in_dir2

# Specifica i percorsi delle due cartelle
cartella1 = r"C:\Users\Admin\Desktop\streamfab_6.1.9.8\StreamFab\App\StreamFab"
cartella2 = r"C:\Program Files\StreamFab\StreamFab"

# Confrontiamo le cartelle
files_in_cartella1_non_in_cartella2, files_in_cartella2_non_in_cartella1 = compare_directories(cartella1, cartella2)

# Stampa i risultati
print(f"File presenti in {cartella1} ma non in {cartella2}:")
for file in files_in_cartella1_non_in_cartella2:
    print(file)

#print(f"\nFile presenti in {cartella2} ma non in {cartella1}:")
#for file in files_in_cartella2_non_in_cartella1:
#    print(file)
