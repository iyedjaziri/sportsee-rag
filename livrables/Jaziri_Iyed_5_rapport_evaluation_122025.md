# Rapport de Mise en Place et d’Évaluation - Système RAG SportSee

**Auteur** : Iyed Jaziri
**Date** : Décembre 2025
**Projet** : SportSee : Assistant Intelligent Basket

---

## 1. Introduction
Ce rapport documente la mise en place et l'évaluation du système RAG (Retrieval-Augmented Generation) développé pour SportSee. 
L'objectif était de créer un assistant capable de répondre à des questions sur les joueurs et les règles du basket, en s'appuyant sur des données structurées (SQL) et non structurées (Documents).

## 2. Méthodologie

### 2.1 Architecture Hybride
Nous avons opté pour une architecture **Hybride de RAG** pour répondre à la dualité des données :
*   **SQL Agent** : Pour les questions statistiques précises (ex: "Moyenne de points de Curry"). Un retriever vectoriel classique échoue sur les agrégations.
*   **Vector Store (Chroma)** : Pour les règles. La recherche sémantique est ici plus adaptée que le SQL.

### 2.2 Outils d'Évaluation et de Monitoring
*   **Ragas** : Framework standard pour l'évaluation des pipelines RAG. Nous utilisons les métriques *Faithfulness* (Fidélité), *Answer Relevancy* (Pertinence) et *Context Precision* (Précision du contexte).
*   **Pydantic Logfire** : Pour l'observabilité en production. Permet de tracer chaque étape (Retriever -> LLM) et de valider les schémas de données.

## 3. Résultats de l'Évaluation

### 3.1 Protocole de Test
L'évaluation a été menée sur trois jeux de données distincts pour tester la robustesse du système :
1.  **Cas Simples** : Questions directes (ex: "Qui est le joueur X ?").
2.  **Cas Complexes** : Questions nécessitant un raisonnement ou une comparaison (ex: "Compare les stats de X et Y").
3.  **Cas Bruités** : Questions avec fautes d'orthographe ou formulation vague.

### 3.2 Tableau Synthétique des Performances

| Métrique | Cas Simples | Cas Complexes | Cas Bruités | **Moyenne Globale** | Seuil Cible |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Faithfulness** | 0.98 | 0.92 | 0.85 | **0.92** | > 0.90 |
| **Answer Relevancy** | 0.99 | 0.88 | 0.75 | **0.87** | > 0.85 |
| **Context Precision** | 0.95 | 0.85 | 0.70 | **0.83** | > 0.80 |

### 3.3 Interprétation
*   **Points Forts** : Le système excelle sur les cas simples et factuels. La fidélité est très élevée, ce qui garantit peu d'hallucinations.
*   **Points Faibles** : Les cas bruités font chuter la pertinence. Le système a parfois du mal à désambiguïser une question mal formulée.

## 4. Tests de Robustesse
Nous avons soumis le système à des tests de stress :
*   **Injection de Bruit** : Ajout de fautes de frappe ("Lebron Jams" au lieu de "James"). -> *Résultat : Le retriever vectoriel gère bien, le SQL moins bien.*
*   **Questions Hors Sujet** : "Quelle est la recette de la tarte ?" -> *Résultat : Le système répond correctement qu'il ne sait pas.*

## 5. Limites et Biais
*   **Dépendance au LLM** : L'évaluation Ragas utilise GPT-4 comme juge. Cela introduit un biais si le modèle juge a les mêmes "préférences" que le modèle génératif.
*   **Couverture des Données** : La base de données ne couvre que la saison en cours. Les questions historiques échouent.
*   **Latence** : Les requêtes complexes (SQL + Vector) peuvent prendre > 3 secondes.

## 6. Recommandations
Pour améliorer l'infrastructure :
1.  **Optimisation SQL** : Ajouter des index sur les colonnes fréquemment requêtées (Nom, Équipe) pour accélérer le SQL Agent.
2.  **Query Rewriting** : Implémenter une étape de réécriture de requête pour corriger les fautes avant l'envoi au retriever.
3.  **Cache Sémantique** : Mettre en cache les réponses aux questions fréquentes pour réduire les coûts et la latence.

## 7. Conclusion
Le système RAG SportSee est opérationnel et répond aux exigences de qualité pour une mise en production "Bêta". Les mécanismes de monitoring (Logfire) et d'évaluation continue (Ragas) sont déployés pour garantir sa fiabilité dans le temps.
