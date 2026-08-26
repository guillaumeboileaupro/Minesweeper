# Démineur

[![Tests](https://github.com/guillaumeboileaupro/Minesweeper/actions/workflows/tests.yml/badge.svg)](https://github.com/guillaumeboileaupro/Minesweeper/actions/workflows/tests.yml)
[![Paquet Ubuntu](https://github.com/guillaumeboileaupro/Minesweeper/actions/workflows/build-ubuntu.yml/badge.svg)](https://github.com/guillaumeboileaupro/Minesweeper/actions/workflows/build-ubuntu.yml)

Jeu de Démineur dans la même identité que les projets Mastermind et Puissance 4 : interface moderne et plate, backend FastAPI, stockage SQLite et application installable sur Ubuntu avec pywebview.

![Logo Démineur](static/demineur.svg)

## Fonctionnalités

- niveaux Débutant (9 × 9, 10 mines), Intermédiaire (16 × 16, 40 mines) et Expert (16 × 30, 99 mines) ;
- grille personnalisée de 5 à 30 lignes et de 5 à 40 colonnes ;
- premier clic et cases voisines toujours sécurisés ;
- dévoilement automatique des zones vides ;
- clic droit pour poser un drapeau et bouton Drapeau pour les écrans tactiles ;
- reprise automatique de la partie en cours ;
- chronomètre, score, statistiques et historique persistants ;
- aide intégrée et interface responsive ;
- version web et application Ubuntu partageant exactement le même jeu.

## Démarrage rapide

Prérequis : Python 3.10 ou plus récent.

```bash
git clone https://github.com/guillaumeboileaupro/Minesweeper.git
cd Minesweeper
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Ouvrir ensuite [http://127.0.0.1:8000](http://127.0.0.1:8000).

## Règles

Chaque case cachée contient une mine ou une zone sûre. Un clic sur une case sûre affiche le nombre de mines présentes dans ses huit cases voisines. Une case sans mine voisine dévoile automatiquement la zone sûre qui l’entoure.

Le clic droit pose ou retire un drapeau. Sur mobile, sélectionner d’abord **Drapeau**, puis toucher la case. Les drapeaux servent d’aide : pour gagner, il faut révéler toutes les cases sans mine. Cliquer sur une mine termine la partie.

Les mines ne sont placées qu’au premier clic. La case choisie et, quand la taille le permet, ses huit voisines sont protégées.

## Comment le code fonctionne

1. FastAPI sert l’interface de `static/` et expose l’API HTTP.
2. `static/app.js` affiche la grille et envoie les actions Révéler/Drapeau.
3. `app/game.py` place les mines, calcule les nombres voisins, propage les zones vides et détecte la victoire.
4. `app/storage.py` conserve la partie, les statistiques et l’historique dans SQLite.

Le frontend ne connaît jamais la position des mines pendant une partie active : l’API masque cette information. Le backend reste donc l’unique source de vérité.

## API principale

| Méthode | Route | Rôle |
| --- | --- | --- |
| `GET` | `/api/config` | Niveaux disponibles |
| `GET` | `/api/games/current` | Partie active |
| `POST` | `/api/games` | Nouvelle partie |
| `POST` | `/api/games/{id}/actions` | Révéler ou marquer une case |
| `POST` | `/api/games/{id}/give-up` | Abandonner |
| `GET` | `/api/stats` | Statistiques |
| `GET` | `/api/history` | Historique |

## Application desktop Ubuntu

```bash
python -m pip install -r requirements-desktop.txt
python desktop.py
```

Construction du paquet Debian :

```bash
bash packaging/build-deb.sh
sudo apt install ./dist/demineur_0.1.0_amd64.deb
```

Les données sont enregistrées dans `~/.local/share/demineur/demineur.db`. En développement, le chemin peut être remplacé avec `DEMINEUR_DB`.

## Tests et qualité

```bash
python -m pip install -r requirements-dev.txt
pytest
mypy
```

## Architecture

```text
Minesweeper/
├── app/
│   ├── game.py
│   ├── main.py
│   ├── storage.py
│   └── types.py
├── static/
│   ├── app.js
│   ├── index.html
│   ├── style.css
│   └── demineur.svg
├── packaging/
├── tests/
├── desktop.py
└── demineur.spec
```
