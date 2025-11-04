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

## Utilisation rapide (M1)

Le jalon M1 ajoute la physique temps réel (intégration 120 Hz), les collisions balle-balle, les murs d'arène (cercle + stadium)
et les bumpers. Les configurations YAML définissent désormais les équipes, les positions initiales et les vitesses.

```bash
python cli.py --scene scenes/circle_basic.yaml --seed 42 --out out/m1_circle.mp4
```

Pour visualiser la simulation pendant l'export (si `pygame` est installé), ajoutez `--show` :

```bash
python cli.py --scene scenes/stadium_basic.yaml --out out/m1_stadium.mp4 --show
```

### Structure d'une scène

```yaml
name: "Circle Basic"
duration_seconds: 12
frame_rate: 30
arena:
  type: "circle"
  radius: 8.0
  bumpers:
    - position: [0.0, 0.0]
      radius: 1.2
teams:
  - name: "Team A"
    color: "#FF5BE1"
    players:
      - name: "A1"
        spawn: [-3.5, -1.75]
        velocity: [4.2, 2.2]
  - name: "Team B"
    color: "#5BD8FF"
    players:
      - name: "B1"
        spawn: [3.5, -1.75]
        velocity: [-4.0, 2.0]
ball_radius: 0.45
ball_mass: 1.0
friction: 0.995
restitution: 0.98
```

Le rendu s'effectue en 1080×1920, 30 fps et respecte la durée définie. Chaque frame combine la simulation et un rendu 2D stylisé
avec l'arène, les bumpers et les balles colorées par équipe.

