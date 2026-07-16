# Rapport de projet — Pipeline AQI

*(Template à compléter par les 5 membres du groupe)*

## 1. Méthode de travail du groupe

- Outils de coordination utilisés (ex: Discord, Trello, réunions...)
- Fréquence des points d'équipe
- Convention de commits / branches Git utilisée

## 2. Répartition des tâches

| Membre | Tâches principales |
|---|---|
| ... | ex: collecte + backfill |
| ... | ex: transformation clean/ + validation |
| ... | ex: modélisation + chargement warehouse |
| ... | ex: orchestrateur GitHub Actions + secrets |
| ... | ex: README, ARCHITECTURE.md, vidéo de démo |

## 3. Difficultés rencontrées et solutions

- ex: rate-limit de l'API gratuite pendant le backfill → ajout d'un `time.sleep`
  entre les appels et découpage en tranches de 30 jours
- ex: ...

## 4. Choix techniques justifiés

Voir [`ARCHITECTURE.md`](ARCHITECTURE.md) pour la table de justifications
détaillée (orchestrateur, stockage, base de données, modélisation).

Compléments éventuels ici : alternatives envisagées et pourquoi elles ont été
écartées.

## 5. Preuves d'exécution automatique

- Lien vers l'onglet *Actions* du repo GitHub, montrant plusieurs runs réussis
  sur au moins 5 jours différents, à des heures sans intervention humaine
- Captures d'écran à inclure ici ou en annexe
