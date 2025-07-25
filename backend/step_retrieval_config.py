"""
Configuration de la récupération RAG par étape 8D
Ce module définit pour chaque étape 8D :
1. Quels champs de la NC actuelle utiliser pour la recherche de similarité
2. Quels champs récupérer dans les NCs similaires trouvées
3. Quels champs de contexte garder pour le LLM
"""

from typing import Dict, List, Optional

class StepRetrievalConfig:
    """Configuration pour la récupération RAG selon l'étape 8D"""
    
    def __init__(self):
        self.config = {
            "d0_initialisation": {
                "search_fields": {
                    # EXPERT 8D: Pour D0, chercher des patterns de détection similaires
                    "from_current_nc": [
                        "produitRef",  # Famille produit = types de défauts récurrents
                        "descriptionInitiale",  # Symptômes observés
                        "LieuDetection",  # Environnement de production (ligne, poste)
                        "FonctionCrea"  # Profil détecteur (QC, Production, Client...)
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Récupérer les infos pour aider la caractérisation initiale
                    "from_similar_ncs": [
                        "Criticite",  # Benchmarking de gravité pour des problèmes similaires
                        "descriptionInitiale",  # Vocabulaire technique et descriptions précises
                        "FonctionCrea",  # Profil des détecteurs habituels de ce type de défaut
                        "comment",  # Mode de détection utilisé (visuel, test, contrôle...)
                        "dateDetection",  # Patterns temporels (saisonnalité, équipes...)
                        "qui"  # Origine du défaut pour anticiper l'équipe
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Contexte essentiel pour bien démarrer l'analyse
                    "keep_for_llm": [
                        "referenceNC",  # Référence unique
                        "descriptionInitiale",  # Symptômes actuels
                        "produitRef",  # Produit impacté
                        "LieuDetection",  # Lieu de détection
                        "dateDetection",  # Timing
                        "detectePar",  # Qui a détecté
                        "FonctionCrea"  # Fonction du détecteur
                    ]
                }
            },
            
            "d1_team": {
                "search_fields": {
                    # EXPERT 8D: Composition d'équipe basée sur complexité et compétences requises
                    "from_current_nc": [
                        "produitRef",  # Complexité technique du produit
                        "descriptionInitiale",  # Type de problème = compétences nécessaires
                        "Criticite",  # Niveau urgence = séniorité équipe requise
                        "LieuDetection",  # Disponibilité locale des ressources
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Récupérer compositions d'équipes qui ont réussi
                    "from_similar_ncs": [
                        "chefEquipe",  # Leadership adapté au type de problème
                        "membresEquipe",  # Composition optimale pour ce type de NC
                        "teamFunction",  # Fonctions clés représentées
                        "Criticite",  # Dimensionnement équipe vs gravité
                        "causesRacinesIdentifiees",  # Complexité cause = équipe renforcée
                        "dateDetection"  # Délai résolution réalisé avec cette équipe
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Informations pour sélection optimale équipe
                    "keep_for_llm": [
                        "referenceNC",
                        "descriptionInitiale",  # Nature du problème
                        "produitRef",  # Expertise produit requise
                        "Criticite",  # Urgence et niveau décisionnel
                        "LieuDetection",  # Contraintes géographiques
                        "detectePar",  # Initiateur disponible pour équipe
                        "FonctionCrea",  # Perspective initiale déjà acquise
                        "qui",  # Cible d'investigation
                        "quoi"  # Périmètre technique
                    ]
                }
            },
            
            "d2_problem": {
                "search_fields": {
                    # EXPERT 8D: Recherche patterns QQOQCCP pour structurer l'analyse
                    "from_current_nc": [
                        "produitRef",  # Même famille produit = modes de défaillance similaires
                        "descriptionInitiale",  # Symptômes = questionnement similaire
                        "LieuDetection",  # Environnement = contraintes opérationnelles
                        "qui",  # Profil responsable = questions adaptées
                        "comment"  # Mode détection = investigation similaire
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Récupérer analyses QQOQCCP complètes et efficaces
                    "from_similar_ncs": [
                        "descriptionDetaillee",  # QQOQCCP complet comme modèle
                        "qui",  # Patterns de responsabilité
                        "quoi",  # Spécifications techniques impactées
                        "ou",  # Localisation précise problème
                        "quand",  # Patterns temporels
                        "comment",  # Modes de défaillance
                        "combien",  # Ampleur quantifiée
                        "pourquoi",  # Impact client/process
                        "actions3D"  # Actions immédiates qui ont suivi
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Base solide pour analyse structurée
                    "keep_for_llm": [
                        "referenceNC",
                        "descriptionInitiale",  # Point de départ
                        "produitRef",  # Spécifications produit
                        "LieuDetection",  # Environnement opérationnel
                        "chefEquipe",  # Leadership de l'analyse
                        "membresEquipe",  # Expertise mobilisée
                        "dateDetection",  # Chronologie importante
                        "Criticite"  # Niveau de détail requis
                    ]
                }
            },
            
            "d3_containment": {
                "search_fields": {
                    # EXPERT 8D: Actions de containment urgentes et efficaces
                    "from_current_nc": [
                        "Criticite",  # Urgence = type d'action containment
                        "produitRef",  # Contraintes techniques de containment
                        "quoi",  # Composant exact = action précise
                        "qui",  # Responsable défaut = action corrective immédiate
                        "pourquoi",  # Impact client = niveau containment requis
                        "combien",  # Ampleur = ressources containment
                        "LieuDetection"  # Localisation = faisabilité actions
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Actions de sécurisation qui ont marché
                    "from_similar_ncs": [
                        "actions3D",  # Actions de containment éprouvées
                        "responsableAction3D",  # Qui peut exécuter efficacement
                        "etatAvancement3D",  # REX sur mise en œuvre
                        "dateDetection",  # Délai réaction pour containment
                        "Criticite",  # Proportionnalité action/gravité
                        "validationResults",  # Efficacité containment mesurée
                        "qui",  # Patterns de responsabilité pour containment
                        "combien"  # Dimensionnement action
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Contexte pour action containment optimale
                    "keep_for_llm": [
                        "referenceNC",
                        "descriptionInitiale",  # Nature du problème
                        "Criticite",  # Urgence absolue
                        "descriptionDetaillee",  # QQOQCCP = base action
                        "chefEquipe",  # Décideur containment
                        "membresEquipe",  # Ressources disponibles
                        "LieuDetection",  # Contraintes terrain
                        "dateDetection",  # Fenêtre temporelle critique
                        "produitRef"  # Contraintes techniques
                    ]
                }
            },
            
            "d4_rootcause": {
                "search_fields": {
                    # EXPERT 8D: Recherche causes racines par patterns techniques
                    "from_current_nc": [
                        "produitRef",  # Famille produit = modes défaillance connus
                        "qui",  # Profil responsable = causes humaines récurrentes
                        "quoi",  # Composant = causes techniques spécifiques
                        "comment",  # Mode détection = nature de la défaillance
                        "ou",  # Environnement = causes externes/process
                        "quand",  # Timing = causes liées aux conditions
                        "pourquoi",  # Impact = sévérité pour profondeur analyse
                        "actions3D"  # Efficacité containment = vraie cause masquée?
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Méthodes d'analyse et causes trouvées
                    "from_similar_ncs": [
                        "causesRacinesIdentifiees",  # Causes validées pour cas similaires
                        "ishikawaData",  # Méthodes 5M utilisées efficacement
                        "fiveWhysData",  # Questionnement 5 Pourquoi pertinent
                        "qui",  # Patterns de causalité humaine
                        "quoi",  # Défaillances techniques récurrentes
                        "comment",  # Modes de défaillance identifiés
                        "actions3D",  # Si containment inefficace = autre cause
                        "validationResults"  # Validation méthode d'analyse
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Contexte pour analyse approfondie
                    "keep_for_llm": [
                        "referenceNC",
                        "descriptionInitiale",  # Symptômes à analyser
                        "descriptionDetaillee",  # Base QQOQCCP complète
                        "actions3D",  # Actions containment déjà prises
                        "chefEquipe",  # Leadership analyse
                        "membresEquipe",  # Expertise technique mobilisée
                        "Criticite",  # Profondeur analyse requise
                        "produitRef",  # Spécifications techniques
                        "LieuDetection"  # Contraintes environnementales
                    ]
                }
            },
            
            "d5_correctiveactions": {
                "search_fields": {
                    # EXPERT 8D: Actions correctives ciblées selon cause racine
                    "from_current_nc": [
                        "causesRacinesIdentifiees",  # Cause = type action spécifique
                        "produitRef",  # Contraintes techniques pour action
                        "LieuDetection",  # Faisabilité locale de l'action
                        "qui",  # Cible de l'action corrective
                        "Criticite",  # Robustesse action requise
                        "chefEquipe"  # Autorité pour mise en œuvre action
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Actions correctives validées et efficaces
                    "from_similar_ncs": [
                        "correctiveActionsData",  # Actions systémiques éprouvées
                        "responsable5D",  # Qui peut porter l'action
                        "service5D",  # Ressources organisationnelles
                        "causesRacinesIdentifiees",  # Cohérence cause-action
                        "validationResults",  # Efficacité mesurée des actions
                        "implementedActions",  # REX mise en œuvre
                        "ishikawaData",  # Actions par famille de cause (5M)
                        "dateDetection"  # Délai réalisation action
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Contexte pour actions correctives pertinentes
                    "keep_for_llm": [
                        "referenceNC",
                        "causesRacinesIdentifiees",  # Base de l'action
                        "descriptionInitiale",  # Problème à résoudre
                        "ishikawaData",  # Analyse 5M pour actions ciblées
                        "fiveWhysData",  # Profondeur causalité
                        "chefEquipe",  # Responsable décision
                        "membresEquipe",  # Ressources disponibles
                        "Criticite",  # Niveau d'action requis
                        "LieuDetection"  # Contraintes mise en œuvre
                    ]
                }
            },
            
            "d6_implementvalidate": {
                "search_fields": {
                    # EXPERT 8D: Validation efficacité et mise en œuvre réussie
                    "from_current_nc": [
                        "correctiveActionsData",  # Type d'action = méthode validation
                        "causesRacinesIdentifiees",  # Cause = indicateur pertinent
                        "Criticite",  # Niveau validation requis
                        "LieuDetection",  # Contraintes validation terrain
                        "produitRef",  # Métriques produit pour validation
                        "qui"  # Cible action = mesure efficacité
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Méthodes validation et résultats probants
                    "from_similar_ncs": [
                        "implementedActions",  # Actions réellement mises en œuvre
                        "validationResults",  # Preuves d'efficacité
                        "responsableAction6D",  # Qui valide efficacement
                        "surveillancePlan",  # Suivi long terme
                        "correctiveActionsData",  # Cohérence action-validation
                        "preventiveActions",  # Si validation OK = passage au 7D
                        "etatAvancement3D",  # Comparaison containment vs corrective
                        "causesRacinesIdentifiees"  # Validation cohérence cause-effet
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Base pour validation robuste
                    "keep_for_llm": [
                        "referenceNC",
                        "correctiveActionsData",  # Actions à valider
                        "causesRacinesIdentifiees",  # Objectif validation
                        "descriptionInitiale",  # Problème initial à résoudre
                        "actions3D",  # Actions containment pour comparaison
                        "chefEquipe",  # Responsable validation
                        "Criticite",  # Rigueur validation requise
                        "ishikawaData",  # Méthode d'analyse pour indicateurs
                        "LieuDetection"  # Contraintes terrain validation
                    ]
                }
            },
            
            "d7_preventrecurrence": {
                "search_fields": {
                    # EXPERT 8D: Prévention systémique de la récurrence
                    "from_current_nc": [
                        "causesRacinesIdentifiees",  # Famille cause = prévention adaptée
                        "validationResults",  # Efficacité corrective = base prévention
                        "ishikawaData",  # 5M = prévention multi-dimensionnelle
                        "produitRef",  # Extension prévention famille produit
                        "LieuDetection",  # Périmètre géographique prévention
                        "qui",  # Profile/poste = prévention formation/process
                        "chefEquipe"  # Leadership pour déploiement systémique
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Actions préventives systémiques réussies
                    "from_similar_ncs": [
                        "preventiveActions",  # Actions préventives éprouvées
                        "documentationUpdates",  # Mise à jour systèmes qualité
                        "systemicChanges",  # Changements organisationnels
                        "causesRacinesIdentifiees",  # Cohérence cause-prévention
                        "surveillancePlan",  # Surveillance continue efficace
                        "responsableAction7D",  # Qui porte prévention systémique
                        "leconsApprises",  # Capitalisation d'expérience
                        "validationResults"  # Preuves d'efficacité préventive
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Vision complète pour prévention systémique
                    "keep_for_llm": [
                        "referenceNC",
                        "causesRacinesIdentifiees",  # Base prévention
                        "correctiveActionsData",  # Actions correctives validées
                        "implementedActions",  # Mise en œuvre réussie
                        "validationResults",  # Efficacité mesurée
                        "chefEquipe",  # Leadership déploiement
                        "membresEquipe",  # Expertise mobilisable
                        "ishikawaData",  # Analyse systémique 5M
                        "surveillancePlan"  # Continuité prévention
                    ]
                }
            },
            
            "d8_congratulate": {
                "search_fields": {
                    # EXPERT 8D: Clôture et capitalisation d'expérience
                    "from_current_nc": [
                        "Criticite",  # Niveau problème = type reconnaissance
                        "causesRacinesIdentifiees",  # Complexité = valorisation équipe
                        "preventiveActions",  # Impact systémique = communication
                        "chefEquipe",  # Leadership = reconnaissance managériale
                        "validationResults",  # Succès mesurable = célébration
                        "produitRef",  # Impact métier = visibilité résultats
                        "LieuDetection"  # Périmètre impact = diffusion REX
                    ]
                },
                "retrieve_fields": {
                    # EXPERT 8D: Bonnes pratiques clôture et REX
                    "from_similar_ncs": [
                        "resumeResultats",  # Synthèse réussites pour communication
                        "leconsApprises",  # Capitalisation expérience transférable
                        "team_recognition",  # Modalités reconnaissance équipe
                        "preventiveActions",  # Impact systémique réalisé
                        "validationResults",  # Preuves succès quantifiées
                        "systemicChanges",  # Changements pérennes réalisés
                        "dateCloture",  # Délai résolution pour benchmark
                        "chefEquipe"  # Leadership reconnu pour autres projets
                    ]
                },
                "context_fields": {
                    # EXPERT 8D: Bilan complet pour clôture valorisante
                    "keep_for_llm": [
                        "referenceNC",
                        "descriptionInitiale",  # Problème initial résolu
                        "causesRacinesIdentifiees",  # Complexité maîtrisée
                        "correctiveActionsData",  # Solutions apportées
                        "preventiveActions",  # Impact systémique
                        "validationResults",  # Preuves d'efficacité
                        "chefEquipe",  # Leadership à valoriser
                        "membresEquipe",  # Équipe à reconnaître
                        "Criticite",  # Enjeu initial vs résultat
                        "surveillancePlan"  # Pérennité assurée
                    ]
                }
            }
        }
    
    def get_config_for_step(self, step_name: str) -> Dict:
        """Récupère la configuration pour une étape donnée"""
        return self.config.get(step_name, self.config["d0_initialisation"])
    
    def get_search_fields(self, step_name: str) -> List[str]:
        """Récupère les champs à utiliser pour la recherche"""
        config = self.get_config_for_step(step_name)
        return config["search_fields"]["from_current_nc"]
    
    def get_retrieve_fields(self, step_name: str) -> List[str]:
        """Récupère les champs à extraire des NCs similaires"""
        config = self.get_config_for_step(step_name)
        return config["retrieve_fields"]["from_similar_ncs"]
    
    def get_context_fields(self, step_name: str) -> List[str]:
        """Récupère les champs de contexte à garder pour le LLM"""
        config = self.get_config_for_step(step_name)
        return config["context_fields"]["keep_for_llm"]

# Instance globale
step_retrieval_config = StepRetrievalConfig()
