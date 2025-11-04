# Power Pit Videos

Power Pit génère des clips verticaux où deux équipes de balles s'affrontent dans des arènes 2D modulaires.

Ce dépôt suit la feuille de route décrite dans [`roadmap.md`](./roadmap.md). Chaque jalon construit progressivement un pipeline complet allant de la simulation au rendu vidéo puis au batch.

## Installation

Créez un environnement Python (3.11+) et installez les dépendances listées dans [`pyproject.toml`](./pyproject.toml) :

```bash
uv venv
uv pip install -e .
```

Pour `pip`, utilisez :

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Utilisation rapide (M0)

Le jalon M0 exporte un clip MP4 noir issu d'une scène YAML.

```bash
python cli.py --scene scenes/circle_basic.yaml --seed 42 --out out/m0_demo.mp4
```

Le fichier d'entrée décrit la scène (nom, arène, durée). Les jalons suivants enrichiront progressivement la simulation, le rendu et les fonctionnalités de batch.

