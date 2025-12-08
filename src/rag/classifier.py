"""
Module de classification des requêtes pour déterminer si une question nécessite RAG
"""

import re
import logging
from typing import Tuple, Optional
from mistralai.client import MistralClient
from mistralai.models.chat_completion import ChatMessage

from src.core.config import settings

# Adapt config access
MISTRAL_API_KEY = settings.MISTRAL_API_KEY
CHAT_MODEL = "mistral-small-latest" # Or "mistral-large-latest" depending on preference
COMMUNE_NAME = "SportSee" # Adapted for this project

logger = logging.getLogger(__name__)

class QueryClassifier:
    """
    Classe pour classifier les requêtes et déterminer si elles nécessitent RAG
    """
    
    def __init__(self):
        """
        Initialise le classificateur de requêtes
        """
        self.mistral_client = MistralClient(api_key=MISTRAL_API_KEY) if MISTRAL_API_KEY else None
        
        # Mots-clés liés à SportSee/Basketball
        self.commune_keywords = [
            COMMUNE_NAME.lower(),
            "nba", "basketball", "basket", "player", "joueur",
            "stats", "statistiques", "points", "rebonds", "assists",
            "match", "game", "team", "équipe", "saison",
            "règles", "rules", "arbitrage", "faute",
            "histoire", "history", "record", "champion",
            "lebron", "curry", "jordan", "kobe", # Examples
            "3pm", "fg%", "minutes"
        ]
        
        # Questions générales qui ne nécessitent pas de RAG
        self.general_patterns = [
            r"^(bonjour|salut|hello|coucou|hey|bonsoir)[\s\.,!]*$",
            r"^(merci|thanks|thank you|je te remercie)[\s\.,!]*$",
            r"^(comment ça va|ça va|comment vas-tu|comment allez-vous)[\s\.,!?]*$",
            r"^(au revoir|bye|à bientôt|à plus tard|à la prochaine)[\s\.,!]*$",
            r"^(qui es[- ]tu|qu'es[- ]tu|que fais[- ]tu|comment fonctionnes[- ]tu|tu es quoi)[\s\?]*$",
            r"^(aide|help|sos|besoin d'aide)[\s\.,!?]*$"
        ]
    
    def needs_rag(self, query: str) -> Tuple[bool, float, str]:
        """
        Détermine si une requête nécessite RAG
        
        Args:
            query: Requête de l'utilisateur
            
        Returns:
            Tuple (besoin_rag, confiance, raison)
        """
        # Convertir la requête en minuscules pour la comparaison
        query_lower = query.lower()
        
        # 1. Vérifier les patterns de questions générales (salutations, remerciements, etc.)
        for pattern in self.general_patterns:
            if re.match(pattern, query_lower):
                return False, 0.95, "Question générale ou salutation"
        
        # 2. Vérifier la présence de mots-clés liés au domaine
        commune_keywords_found = [kw for kw in self.commune_keywords if kw in query_lower]
        if commune_keywords_found:
            keywords_str = ", ".join(commune_keywords_found)
            return True, 0.9, f"Contient des mots-clés liés au domaine: {keywords_str}"
        
        # 3. Utiliser le LLM pour les cas ambigus
        if self.mistral_client:
            return self._classify_with_llm(query)
        
        # Par défaut, utiliser RAG pour les questions longues (plus de 5 mots)
        words = query.split()
        if len(words) > 5:
            return True, 0.6, "Question complexe (plus de 5 mots)"
        
        # Par défaut, ne pas utiliser RAG
        return False, 0.5, "Aucun critère spécifique détecté"
    
    def _classify_with_llm(self, query: str) -> Tuple[bool, float, str]:
        """
        Utilise le LLM pour classifier la requête
        
        Args:
            query: Requête de l'utilisateur
            
        Returns:
            Tuple (besoin_rag, confiance, raison)
        """
        try:
            system_prompt = f"""Vous êtes un classificateur de requêtes pour un assistant virtuel de {COMMUNE_NAME} (Basketball Analytics).
Votre tâche est de déterminer si une question nécessite une recherche dans une base de connaissances (stats, règles).

Répondez UNIQUEMENT par "RAG" ou "DIRECT" suivi d'une brève explication:
- "RAG" si la question porte sur des stats, des joueurs, des règles ou des infos NBA.
- "DIRECT" si c'est une question générale, une salutation, ou hors sujet de la NBA.

Exemples:
Question: "Bonjour, comment ça va?"
Réponse: DIRECT - Simple salutation

Question: "Combien de points a marqué LeBron?"
Réponse: RAG - Demande de stats

Question: "Quelles sont les règles du marché?"
Réponse: RAG - Demande de règles
"""
            
            messages = [
                ChatMessage(role="system", content=system_prompt),
                ChatMessage(role="user", content=query)
            ]
            
            response = self.mistral_client.chat(
                model=CHAT_MODEL,
                messages=messages,
                temperature=0.1,  # Température basse pour des réponses cohérentes
                max_tokens=50  # Réponse courte suffisante
            )
            
            result = response.choices[0].message.content.strip()
            logger.info(f"Classification LLM pour '{query}': {result}")
            
            # Analyser la réponse
            if result.startswith("RAG"):
                confidence = 0.85  # Confiance élevée dans la décision du LLM
                reason = result.replace("RAG - ", "").replace("RAG-", "").replace("RAG:", "").strip()
                return True, confidence, reason
            elif result.startswith("DIRECT"):
                confidence = 0.85
                reason = result.replace("DIRECT - ", "").replace("DIRECT-", "").replace("DIRECT:", "").strip()
                return False, confidence, reason
            else:
                # Réponse ambiguë, utiliser RAG par défaut
                return True, 0.6, "Classification ambiguë, utilisation de RAG par précaution"
                
        except Exception as e:
            logger.error(f"Erreur lors de la classification avec LLM: {e}")
            # En cas d'erreur, utiliser RAG par défaut
            return True, 0.5, f"Erreur de classification: {str(e)}"
