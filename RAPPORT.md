# RAPPORT DE PROJET - DONNEES2
## Pipeline Qualité de l'Air (AQI) & Data Warehouse
**Formation :** Écosystème Logiciel / HEI  
**Date de rendu :** Samedi 1er août 2026  

---

### 1. Méthode de travail du groupe
Pour mener à bien le déploiement continu du pipeline de données sur un rythme $24h/24$, le groupe a adopté une approche collaborative axée sur les bonnes pratiques DevOps et le versionnage Git.

* **Versionnage & Stratégie Git :** Utilisation d'un workflow basé sur des branches de fonctionnalités (`feature/*`, `docs/*`) et une branche d'intégration `preprod`. Isolation stricte des secrets : aucun mot de passe ni clé d'API n'a été commité grâce à un fichier `.env` ignoré via `.gitignore`.
* **Coordination :** Synchronisation de l'équipe pour définir le Contrat de Données (format des JSON bruts dans `données/raw/`, schéma du CSV unique `données/clean/` et modélisation SQL).

---

### 2. Répartition des Tâches (Qui a fait quoi)

* **harena (tsutoru) :** Initialisation de la structure du projet, nettoyage et refactorisation du code (*clean the quality of the code*), sécurisation du dépôt (exclusion des fichiers `.env` dans `.gitignore`) et première mise en place de l'orchestration.
* **nomena / nomena-yves :** Implémentation du chargement dynamique des variables d'environnement (`load_dotenv`), exécution et automatisation du backfill initial de 90 jours sur les 5 villes, gestion de la reconstruction de la zone `clean/` et configuration des workflows **GitHub Actions 24h/24**.
* **ikkikana :** Rédaction, structuration et finalisation de la documentation technique globale du projet dans le fichier `README.md` (spécifications du contrat de données et détails des villes).
* **CHARAFFAINE ISSA BEN SAID (Vylhiz) :** Rédaction et structuration du rapport de projet (`RAPPORT.md`), analyse de la modélisation du Data Warehouse, contrôle de la conformité du pipeline et préparation des livrables analytiques pour le cours IA1.

---

### 3. Difficultés rencontrées et solutions apportées

| DIFFICULTÉ RENCONTRÉE | ORIGINE/IMPACT | SOLUTION APPORTÉE |
| :--- | :--- | :--- |
| **1. Fuite potentielle de clés API & Secrets** | Risque d'exposition publique des accès OpenWeatherMap et de la base de données. | Séparation stricte via `.env` + injection dynamique dans les secrets GitHub Actions. |
| **2. Risque de doublons temporels dans `clean/`** | Lors des exécutions répétées de l'orchestration, risque de dupliquer les mêmes relevés. | Application du principe de reconstruction intégrale : la zone `clean/` est entièrement régénérée à chaque run depuis la zone immuable `raw/` (garantie d'idempotence). |
| **3. Non-additivité de la mesure AQI** | Impossibilité de sommer les valeurs AQI ou les concentrations de polluants. | Spécification dans la documentation que les requêtes décisionnelles doivent uniquement employer des fonctions d'agrégation `AVG`, `MIN` ou `MAX`. |
| **4. Disponibilité des PC hôtes locaux** | Risque d'interruption du suivi sur 5 jours en cas de veille ou coupure sur les machines locales. | Migration de l'orchestration locale vers **GitHub Actions** pour assurer un suivi automatisé et continu $24h/24$. |

---

### 4. Justification des choix techniques

* **Orchestrateur (GitHub Actions)**  
  Initialement testé sous Apache Airflow, l'orchestration finale a été migrée sur GitHub Actions. Ce choix garantit un pipeline automatisé stable $24h/24$ sur 5 jours sans risquer d'interruptions liées aux contraintes matérielles des PC hôtes locaux (mise en veille, coupures réseau/électriques).

* **Zone `raw/` (JSON)**  
  Assure l'immutabilité des données d'origine. Garantit que le système peut être reconstruit à tout moment (*self-healing*).

* **Zone `clean/` (CSV unique)**  
  Sert de contrat de données clair et facilement vérifiable avant le chargement en base.

* **Data Warehouse (PostgreSQL / Neon - Schéma en Étoile)**  
  Offre une structure dénormalisée simple et performante pour requêter la table de faits (`fact_air_quality`) selon les dimensions temps et ville pour les besoins du cours IA1.
