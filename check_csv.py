import pandas as pd
import os

# Chemin du fichier CSV
csv_path = os.path.join("documents", "NC5_clean.csv")

try:
    # Lire le CSV
    print(f"Tentative de lecture du CSV: {csv_path}")
    df = pd.read_csv(csv_path, sep=';')
    
    # Informations générales
    print(f"Nombre total de lignes: {len(df)}")
    print(f"Colonne d'ID: {df.columns[0]}")
    
    # Afficher les premiers IDs
    print(f"Premiers 5 IDs:")
    for i in range(min(5, len(df))):
        print(f"  {i+1}. {df.iloc[i, 0]}")
    
    # Vérifier l'existence de certains IDs
    ids_to_check = ["NC-630", "630", "NC-001", "001"]
    for id_check in ids_to_check:
        exists = id_check in df.iloc[:, 0].astype(str).tolist()
        print(f"ID '{id_check}' existe: {exists}")
        
        # Si l'ID n'existe pas directement, chercher des correspondances partielles
        if not exists:
            matches = [id_val for id_val in df.iloc[:, 0].astype(str) if id_check in id_val]
            if matches:
                print(f"  Correspondances partielles pour '{id_check}': {matches[:5]}")

except Exception as e:
    print(f"Erreur lors de la lecture du CSV: {e}")
