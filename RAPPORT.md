RAPPORT DE PROJET - DONNEES2
Pipeline Qualite de l Air AQI et Data Warehouse

Groupe : Groupe 21
Formation : Ecosysteme Logiciel / HEI
Date de rendu : Samedi 1er aout 2026


1. Methode de travail du groupe

Pour mener a bien le deploiement continu du pipeline de donnees sur un rythme 24h sur 24, le groupe a adopte une approche collaborative axee sur les bonnes pratiques DevOps et le versionnage Git.

Versionnage et strategie Git : Utilisation d un workflow base sur des branches de fonctionnalites et une branche d integration preprod. Isolation stricte des secrets : aucun mot de passe ni aucune cle d API n a ete commite grace a un fichier .env ignore via .gitignore.

Coordination : Synchronisation de l equipe pour definir le Contrat de Donnees, notamment le format des JSON bruts dans donnees/raw, le schema du CSV unique dans donnees/clean et la modelisation SQL.


2. Repartition des taches

Harena (tsutoru) : Initialisation de la structure du projet, nettoyage et refactorisation du code, securisation du depot avec l exclusion des fichiers .env dans .gitignore et premiere mise en place de l orchestration.

Nomena (nomena-yves) : Implementation du chargement dynamique des variables d environnement avec load_dotenv, execution et automatisation du backfill initial de 90 jours sur les 5 villes, gestion de la reconstruction de la zone clean et configuration des workflows GitHub Actions 24h sur 24.

Ikkikana : Redaction, structuration et finalisation de la documentation technique globale du projet dans le fichier README.md, notamment les specifications du contrat de donnees et les details des villes.

CHARAFFAINE ISSA BEN SAID (Vylhiz) : Redaction et structuration du rapport de projet RAPPORT.md, analyse de la modelisation du Data Warehouse, controle de la conformite du pipeline et preparation des livrables analytiques pour le cours IA1.


3. Difficultes rencontrees et solutions apportees

Difficulte 1 : Fuite potentielle de cles API et de secrets

Origine et impact : Risque d exposition publique des acces OpenWeatherMap et de la base de donnees.

Solution apportee : Separation stricte des secrets via le fichier .env et injection dynamique dans les secrets GitHub Actions.


Difficulte 2 : Risque de doublons temporels dans la zone clean

Origine et impact : Lors des executions repetees de l orchestration, il existe un risque de duplication des metadonnees.

Solution apportee : Application du principe de reconstruction integrale. La zone clean est entierement regeneree a chaque execution a partir de la zone immuable raw, ce qui garantit l idempotence du pipeline.


Difficulte 3 : Non additivite de la mesure AQI

Origine et impact : Impossibilite de sommer directement les valeurs AQI ou les concentrations de polluants.

Solution apportee : Specification dans la documentation que les requetes decisionnelles doivent uniquement utiliser des fonctions d agregation adaptees telles que AVG, MIN ou MAX.


Difficulte 4 : Disponibilite des PC hotes locaux

Origine et impact : Risque d interruption du suivi sur 5 jours en cas de mise en veille ou de coupure sur les machines locales.

Solution apportee : Migration de l orchestration locale vers GitHub Actions afin d assurer un suivi automatise et continu 24h sur 24.


4. Justification des choix techniques

Orchestrateur GitHub Actions

Initialement teste sous Apache Airflow, l orchestration finale a ete migree vers GitHub Actions. Ce choix garantit un pipeline automatise et stable 24h sur 24 pendant 5 jours, sans risquer d interruptions liees aux contraintes materielles des PC hotes locaux, telles que la mise en veille, les coupures reseau ou les coupures electriques.


Zone raw JSON

La zone raw assure l immutabilite des donnees d origine. Elle garantit que le systeme peut etre reconstruit a tout moment a partir des donnees brutes disponibles, ce qui contribue a la resilience et a la capacite de reconstruction du pipeline.


Zone clean CSV unique

La zone clean sert de contrat de donnees clair et facilement verifiable avant le chargement des donnees dans la base de donnees.


Data Warehouse PostgreSQL Neon avec schema en etoile

Le Data Warehouse offre une structure denormalisee, simple et performante pour interroger la table de faits fact_air_quality selon les dimensions du temps et de la ville. Cette modelisation est adaptee aux besoins d analyse et de prise de decision dans le cadre du cours IA1.