import re
from .prompts import (
    rag_8D_prompt,
    prompt_8D_1,
    prompt_8D_2,
    prompt_8D_3,
    prompt_8D_4_main_oeuvre,prompt_8D_4_materiel,prompt_8D_4_matiere,prompt_8D_4_methode,prompt_8D_4_milieu,
    prompt_8D_4_5why,
    prompt_8D_5_corrective,
    prompt_8D_5_preventive,
    prompt_8D_6,
    prompt_8D_7,
    prompt_8D_8,
)
from.prompts_phi4 import (
    prompt_8D_1_template,
    prompt_8D_2_template,
    prompt_8D_3_template,
    prompt_8D_4_main_oeuvre_template,
    prompt_8D_4_materiel_template,
    prompt_8D_4_matiere_template,
    prompt_8D_4_methode_template,
    prompt_8D_4_milieu_template,
    prompt_8D_4_5why_template,
    prompt_8D_5_corrective_template,
)
from .ollama_thinking import ChatOllamaWithThinking


def get_prompt_for_step(step_name: str, user_query: str = ""):
    """
    Retourne le prompt adapté à l'étape 8D sélectionnée.
    Cette fonction remplace la logique de détection automatique par une sélection directe.
    """
    # Mapping direct des étapes vers les prompts
    step_to_prompt = {
        "d0_initialisation": rag_8D_prompt,
        "d1_team": prompt_8D_1,
        "d2_qqoqccp": prompt_8D_2,
        "d2_problem": prompt_8D_2,  # Alias pour compatibilité
        "d3_containment": prompt_8D_3,
        "d4_rootcause": prompt_8D_4_methode,  # Par défaut méthode pour D4
        "d5_correctiveactions": prompt_8D_5_corrective,  # Par défaut corrective pour D5
        "d6_implementvalidate": prompt_8D_6,
        "d7_preventrecurrence": prompt_8D_7,
        "d8_congratulate": prompt_8D_8,
    }
    
    # Cas spéciaux pour D4 selon le contenu de la requête (optionnel)
    if step_name == "d4_rootcause" and user_query:
        query = user_query.lower()
        if "main" in query or "opérateur" in query or "personnel" in query or "humain" in query:
            return prompt_8D_4_main_oeuvre
        elif "matériel" in query or "machine" in query or "équipement" in query or "outil" in query:
            return prompt_8D_4_materiel
        elif "milieu" in query or "environnement" in query or "température" in query:
            return prompt_8D_4_milieu
        elif "matière" in query or "composant" in query or "pièce" in query or "produit" in query:
            return prompt_8D_4_matiere
        elif "pourquoi" in query:
            return prompt_8D_4_5why
    
    # Cas spéciaux pour D5 selon le contenu de la requête (optionnel)
    if step_name == "d5_correctiveactions" and user_query:
        query = user_query.lower()
        if "préventive" in query or "preventive" in query or "empêcher" in query or "prévenir" in query:
            return prompt_8D_5_preventive
    
    # Retourner le prompt correspondant à l'étape ou le prompt par défaut
    return step_to_prompt.get(step_name, rag_8D_prompt)


def detect_prompt(user_query: str, step: str = None):
    """
    Fonction simplifiée qui utilise get_prompt_for_step() si une étape est fournie,
    sinon retourne le prompt par défaut.
    """
    # Si une étape est fournie, utiliser la nouvelle logique
    if step:
        print(f"[ROUTEUR] Sélection directe du prompt pour l'étape: {step}")
        return get_prompt_for_step(step, user_query)
    
    # Sinon, retourner le prompt par défaut
    print(f"[ROUTEUR] Aucune étape fournie, utilisation du prompt par défaut")
    return rag_8D_prompt


# Export des fonctions principales pour l'import depuis d'autres modules
__all__ = ['detect_prompt', 'get_prompt_for_step']
