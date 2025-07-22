"""
Mapping entre les noms de champs de notre configuration et les colonnes du CSV
"""

# Mapping des champs de configuration vers les colonnes réelles du CSV
FIELD_MAPPING = {
    # Champs D0
    "produitRef": "Article impacté (pas de marque et/ou modèle) 0D",
    "descriptionInitiale": "Description du problème 0D",
    "detectePar": "Créateur NC 0D",
    "LieuDetection": "Localisation 0D(Site A, Site B, Site C,Site D)",
    "FonctionCrea": "Fonction Créateur 0D",
    "dateDetection": "Date de Détection 0D(jj/mm/aaaa)",
    "Criticite": "Criticité 0D",
    "referenceNC": "Identification NC 0D",
    
    # Champs individuels QQOQCCP (pour recherche spécifique)
    "qui": "Qui a produit le défaut ? 2D",
    "quoi": "Quoi/Quelle pièce est impactée ? 2D", 
    "ou": "Où la NC s'est produite ? 2D",
    "quand": "Quand ? 2D(jj/mm/aaaa)",
    "comment": "Comment la NC a été détectée ? 2D",
    "combien": "Combien de pièces impactée ? (0000) 2D",
    "pourquoi": "Pourquoi est ce un problème ? 2D",
    
    # Champs D1
    "chefEquipe": "name 1D",
    "membresEquipe": "name 1D",  # Même colonne, contient toute l'équipe
    "teamFunction": "team function 1D",
    "teamContact": "contact  1D(mail,phone num)",
    
    # Champs D2 (QQOQCCP) - mapping complet
    "descriptionDetaillee": {
        "qui": "Qui a produit le défaut ? 2D",
        "quoi": "Quoi/Quelle pièce est impactée ? 2D", 
        "ou": "Où la NC s'est produite ? 2D",
        "quand": "Quand ? 2D(jj/mm/aaaa)",
        "comment": "Comment la NC a été détectée ? 2D",
        "combien": "Combien de pièces impactée ? (0000) 2D",
        "pourquoi": "Pourquoi est ce un problème ? 2D"
    },
    
    # Champs D3
    "actions3D": "Action(s) de sécurisation 3D",
    "responsableAction3D": "Responsable de l'action 3D",
    "etatAvancement3D": "Etat Avancement 3D",
    
    # Champs D4
    "ishikawaData": {
        "moyen": "5Moyen 4D",
        "milieu": "5Milieu 4D", 
        "methodes": "5Méthodes 4D",
        "mainOeuvre": "5Main d'œuvre 4D",
        "matiere": "5Matière 4D"
    },
    "fiveWhysData": {
        "pourquoi1": "Pourquoi N°1 4D",
        "pourquoi2": "Pourquoi N°2 4D",
        "pourquoi3": "Pourquoi N°3 4D", 
        "pourquoi4": "Pourquoi N°4 4D",
        "pourquoi5": "Pourquoi N°5 4D"
    },
    "causesRacinesIdentifiees": "Cause Racine 4D",
    
    # Champs D5
    "correctiveActionsData": "Action(s) systémique(s) 5D",
    "responsable5D": "Responsable 5D",
    "service5D": "Service 5D",
    
    # Champs D6
    "implementedActions": "Action(s) systémique(s) 6D",
    "responsableAction6D": "Responsable de l'action 6D",
    "validationResults": "Le nombre de défaut a t\"il diminué ? 6D",
    
    # Champs D7
    "preventiveActions": "Action(s) préventive(s) systémique(s) 7D",
    "responsableAction7D": "Responsable de l'action 7D",
    
    # Champs D8
    "resumeResultats": "Résumé 8D",
    "leconsApprises": "Résumé avec saut de ligne 8D",  # Plus détaillé
    "dateCloture": "Date de clôture 8D",
    "team_recognition": "name 1D"  # Reconnaissance de l'équipe
}

def get_csv_field_name(config_field_name: str) -> str:
    """
    Convertit un nom de champ de configuration vers le nom de colonne CSV
    """
    mapping = FIELD_MAPPING.get(config_field_name, config_field_name)
    
    # Si c'est un dictionnaire, on retourne le nom du champ (cas complexes)
    if isinstance(mapping, dict):
        return config_field_name
    
    return mapping

def get_qqoqccp_fields() -> dict:
    """Retourne le mapping pour les champs QQOQCCP"""
    return FIELD_MAPPING.get("descriptionDetaillee", {})

def get_ishikawa_fields() -> dict:
    """Retourne le mapping pour les champs Ishikawa"""
    return FIELD_MAPPING.get("ishikawaData", {})

def get_five_whys_fields() -> dict:
    """Retourne le mapping pour les 5 Pourquoi"""
    return FIELD_MAPPING.get("fiveWhysData", {})
