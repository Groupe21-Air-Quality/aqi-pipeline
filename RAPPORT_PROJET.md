# RAPPORT DE PROJET — Exemple de structure (à réécrire avec vos vrais détails)

## 1. Méthode de travail du groupe

> Le groupe s'est organisé autour des échanges quotidiens qui se sont faits sur [Discord/Messenger/autre], avec un point synthèse tous les jours. Le repo GitHub a servi de source unique de vérité pour le code et les données.

## 2. Répartition des tâches


| Membre | Tâche principale |
|---|---|
| FENOMANANJARA Harena Sarobidy | Script de collecte API + config des villes + Airflow(aux debut) + Aide Pipeline Github Action + tests, vidéo de démo + NoteBook (juste un exemple que lui a cree pas pour le groupe)|
| RABEMANANJARA Nomenjanahary Yves | Script de reconstruction clean/ + validation + Pipeline Github Action + Base de donne Neon|
| CHARAFFAÏNE Issa Ben Saïd | Redaction du Rapport.md |
| RANDRIAMIZAKANOMENTSOA Princy | Redaction du README.md |
| RAZAFIKIAZANANY Whinestino Andy Steevel | Redaction de l'ARCHITECTURE.md |

## 3. Difficultés rencontrées et solutions


- **Difficulté** : Airflow en local nécessitait de laisser une machine allumée en continu, incompatible avec l'exigence "tourne après le rendu".
  **Solution** : migration vers GitHub Actions, réutilisation des mêmes scripts Python.

- **Difficulté** : erreur de connexion à Neon (`invalid URI query parameter: "channelBinding"`).
  **Solution** : retrait du paramètre `channelBinding` non supporté par `psycopg2` dans la chaîne de connexion.

- **Difficulté** : `git_commit_push` échouait avec `fatal: detected dubious ownership in repository` dans le conteneur Docker.
  **Solution** : ajout de `git config --global --add safe.directory` dans le Dockerfile.


## 4. Choix techniques justifiés

*Reprenez ici, en les développant un peu plus, les mêmes points que dans ARCHITECTURE.md :*
- Pourquoi OpenWeather plutôt qu'une autre API
- Pourquoi GitHub Actions plutôt qu'Airflow en production
- Pourquoi Neon plutôt qu'une autre base
- Pourquoi un schéma en étoile plutôt qu'en flocon

## 5. Bilan

*Court paragraphe de conclusion : ce qui a bien fonctionné, ce que vous feriez différemment avec plus de temps.*

---

