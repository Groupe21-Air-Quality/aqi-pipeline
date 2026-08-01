# RAPPORT DE PROJET — DONNEES2
**Groupe 21 — Pipeline Qualité de l'Air (AQI) & Data Warehouse**  
*Formation : Écosystème Logiciel / HEI*  
*Date de rendu : Samedi 1er août 2026*

---

## 1. Méthode de travail du groupe

Pour mener à bien le déploiement continu du pipeline de données sur un rythme 24h/24, le groupe a adopté une approche collaborative axée sur les bonnes pratiques DevOps et le versionnage Git.

* **Versionnage & Stratégie Git :**
  * Utilisation d'un workflow basé sur des branches de fonctionnalités (`feature/*`, `docs/*`) et une branche d'intégration **`preprod`**.
  * Isolation stricte des secrets : aucun mot de passe ni clé d'API n'a été commité dans l'historique grâce à un fichier `.env` ignoré via `.gitignore`.
* **Coordination :**
  * Synchronisation de l'équipe pour définir le **Contrat de Données** (format des JSON bruts dans `données/raw/`, schéma du CSV unique `données/clean/` et modélisation SQL).

---

## 2. Répartition des Tâches (Qui a fait quoi)

* **harena (tsutoru) :** Initialisation de la structure du projet, nettoyage et refactorisation du code (`clean the quality of the code`), sécurisation du dépôt (exclusion des fichiers `.env` dans `.gitignore`) et première mise en place du DAG Airflow.
* **nomena / nomena-yves :** Implémentation du chargement dynamique des variables d'environnement (`load_dotenv`), exécution et automatisation du **backfill initial de 90 jours** sur les 5 villes, gestion de la reconstruction de la zone `clean/` et configuration des workflows GitHub Actions / Airflow 24h/24.
* **ikkikana :** Rédaction, structuration et finalisation de la documentation technique globale du projet dans le fichier `README.md` (spécifications du contrat de données et détails des villes).
* **CHARAFFAINE ISSA BEN SAID :** Rédaction et structuration du rapport de projet (`RAPPORT.md`), analyse de la modélisation du Data Warehouse, contrôle de la conformité du pipeline et préparation des livrables analytiques pour le cours IA1.

---

## 3. Difficultés rencontrées et solutions apportées

| Difficulté rencontrée | Origine / Impact | Solution apportée |
| :--- | :--- | :--- |
| **1. Fuite potentielle de clés API & Secrets** | Risque d'exposition publique des accès OpenWeatherMap et de la base de données. | Séparation stricte via `.env` + injection dynamique dans les variables d'environnement de GitHub Actions / Airflow. |
| **2. Risque de doublons temporels dans `clean/`** | Lors des exécutions répétées de l'orchestration, risque de dupliquer les mêmes relevés. | Application du principe de **reconstruction intégrale** : la zone `clean/` est entièrement régénérée à chaque run depuis la zone immuable `raw/` (garantie d'**idempotence**). |
| **3. Non-additivité de la mesure AQI** | Impossibilité de sommer les valeurs AQI ou les concentrations de polluants. | Spécification dans la documentation que les requêtes décisionnelles doivent uniquement employer des fonctions d'agrégation `AVG`, `MIN` ou `MAX`. |

---

## 4. Justification des choix techniques

* **Orchestrateur (Apache Airflow) :** Permet la gestion des dépendances entre tâches, le suivi visuel des exécutions, les retries automatiques et le rattrapage historique (*catchup*).
* **Zone `raw/` (JSON) :** Assure l'**immutabilité** des données d'origine. Garantit que le système peut être reconstruit à tout moment (*self-healing*).
* **Zone `clean/` (CSV unique) :** Sert de contrat de données clair et facilement vérifiable avant le chargement en base.
* **Data Warehouse (PostgreSQL / Neon - Schéma en Étoile) :** Offre une structure dénormalisée simple et performante pour requêter la table de faits (`fact_air_quality`) selon les dimensions temps et ville pour les besoins du cours IA1.
