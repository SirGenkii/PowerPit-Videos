
---

# Power Pit — Roadmap

## 0) Pitch & Format

* **Concept**: arène 2D verticale (9:16). Deux équipes (2v2 au MVP) s’éjectent en se percutant.
* **Lisibilité**: arènes avec **trous de sortie**, **bumpers**, **buffs** (Speed+, Mass+, Life+).
* **Prod**: génération de clips seedables, **1080×1920, 30fps, 8–12s**, palettes néon, overlay score/timer.
* **Objectif vidéo**: “Can Team A clutch before 00:10?” + **near-miss** + **fin satisfaisante** (KO, replay).

---

## 1) Boucle de jeu (MVP)

1. Initialiser l’arène (forme + trous + bumpers), deux équipes 2v2.
2. **Spawns par canons** via trous (angles/vitesses distribués).
3. Physique pas à pas (collisions, bumpers, knockback).
4. Pop aléatoire de buffs (Speed+, Mass+, Life+), ramassage au contact.
5. Détection **KO** (franchissement d’un trou avec élan suffisant). **Effet Smash**.
6. Score / timer, fin de manche → export MP4.

---

## 2) Mécaniques (v1)

### 2.1 Physique & Knockback

* Intégration: semi-implicite Euler/Verlet, `dt ≈ 1/60`.
* Frottement linéaire global `f≈0.995`, restitution défaut `e≈0.98`, bumpers `e≈1.2–1.6`.
* **Knockback** (sur collision balle-balle):

  * `n = normalize(pB - pA)`
  * `v_rel = (vB - vA)`
  * `impulse = K * max(0, dot(v_rel, n)) * (mA/(mB+ε))`
  * Appliquer `± impulse * n` (conserver quantité de mvt globale).
* **Edge assist** (near-KO satisfaisant) : champ radial sortant autour du **centre des trous**:

  * Si distance < `R_edge`, ajouter `F = strength * (1 - d/R_edge) * dir_out`.

### 2.2 KO / Sortie

* KO si **centre** de la balle traverse l’arc d’un trou **et** `speed > v_min_ko`.
* On log l’ID du trou, l’équipe qui score, on trigge VFX/SFX.

### 2.3 Buffs (MVP)

* **Speed+**: `speed *= 1.35` (durée 5s, cap x1.75).
* **Mass+**: `mass *= 1.6` (durée 5s, cap x2.0) ⇒ plus de knockback infligé, moins reçu.
* **Life+**: spawn **1** balle via le **canon le plus distant** des adversaires.
* Spawn cadence: toutes **3–5s**, pondération **comeback** (équipe en retard +20%).

---

## 3) Arènes

### 3.1 Types (MVP)

* **circle** (R, trous par arcs angulaires),
* **stadium** (deux plats + coins arrondis),
* **donut** (anneau, trou central non-KO),
* (Stretch) **polygon** avec arcs de trous sur segments.

### 3.2 Trous & bumpers

* **Trous**: arcs {angle°, width°} avec ID (sert pour canons & KO).
* **Bumpers**: position `(x,y)`, rayon, restitution `e`, teinte.

---

## 4) Spawns “canons”

* Chaque trou peut servir de **canon**:
  `velocity ~ U(v_min, v_max)`, `angle ~ N(mu, sigma)` tangentiel à la sortie.
* **Fairness**: alternance stricte des équipes; **grace 1.0s** après un KO pour éviter spawn-kill.
* **VFX**: lueur 300 ms dans le trou, “poof”.

---

## 5) Pacing

* **Match**: 60–75s, **target_score = 5** ou “plus haut score à fin timer”.
* **Sudden-death**: anneau qui **rétrécit** à `t > 50s`.
* **Buff rate**: 3–5s; en fin de match, +15% de chance d’apparition.

---

## 6) VFX/UX (juice)

* **Hitstop** 80–120 ms sur gros impact, **screenshake** léger (amplitude ∝ impulse).
* Flash blanc très court + **trails** colorés par équipe.
* **KO Smash**: zoom out 6–8%, vignette, particules, son court; **replay 0.75×** (si temps).
* Overlays: timer, score, **seed**, nom d’arène, icônes de buffs actifs sur chaque balle.

---

## 7) Stack technique

* **Physique**: `pymunk` (rigide + murs + bumpers) **ou** maison (cercle/polygones) — MVP ok avec pymunk.
* **Config**: `YAML` (PyYAML).
* **Rendu**: `Pillow`/`pycairo` + glow simple ; export `imageio[ffmpeg]` (MP4 H.264).
* **Audio (later)**: `pydub` (snare/kick KO).
* **Batch**: CLI pour générer N vidéos par seed.

```bash
# Setup
uv venv && uv pip install numpy pillow imageio[ffmpeg] pyyaml pymunk moviepy
# (ou pip classique)
```

---

## 8) Structure projet

```
power-pit/
  README.md
  roadmap.md
  scenes/
    circle_basic.yaml
    stadium_2holes.yaml
  assets/
    palettes.yaml
    sfx/ (optionnel)
  engine/
    arena.py          # formes, trous, bumpers
    physics.py        # intégration, collisions, knockback
    buffs.py          # définitions, états, ramassage
    spawn.py          # canons, fairness
    state.py          # équipe, balles, score
  render/
    renderer.py       # draw, glow, trails, UI, VFX
  cli.py              # run scene -> mp4
  batch.py            # loop de seeds
```

---

## 9) Schéma YAML (v0)

```yaml
seed: 42
duration_s: 60
video: {width: 1080, height: 1920, fps: 30, background: "#06060a"}
arena:
  type: circle           # circle|stadium|donut|polygon
  radius: 480
  holes:                 # arcs (angle_deg, width_deg)
    - {id: H1, angle: 20,  width: 28}
    - {id: H2, angle: 160, width: 32}
  bumpers:
    - {x: -220, y: 180, r: 28, e: 1.4}
    - {x: 240,  y: -120, r: 28, e: 1.5}
spawner:
  cannons:
    - {hole: H1, v_min: 520, v_max: 680, ang_mu: 0, ang_sigma: 22}
    - {hole: H2, v_min: 520, v_max: 680, ang_mu: 0, ang_sigma: 18}
  fairness: alternate_teams
  grace_after_ko_s: 1.0
teams:
  - {name: Alpha, color: "#ff66cc", balls_start: 2, skin: "alpha_neon"}
  - {name: Beta,  color: "#7fe3ff", balls_start: 2, skin: "beta_neon"}
buffs:
  spawn_every_s: [3.0, 5.0]
  types:
    - {id: speed, dur_s: 5, factor: 1.35, weight: 1.0, icon: "S+"}
    - {id: mass,  dur_s: 5, factor: 1.6,  weight: 0.8, icon: "M+"}
    - {id: life,  dur_s: 0, add_ball: 1,  weight: 0.5, icon: "+1"}
physics:
  dt: 0.0167
  friction: 0.995
  restitution: 0.98
  K_knockback: 1.2
  edge_force: {enabled: true, radius_px: 120, strength: 900}
ui:
  target_score: 5
  sudden_death_at_s: 50
```

---

## 10) Pseudocode clés

### Collision & Knockback

```python
if collide(ballA, ballB):
    n = normalize(ballB.pos - ballA.pos)
    v_rel = dot((ballB.vel - ballA.vel), n)
    if v_rel > 0:
        J = K_knockback * v_rel * (ballA.mass / (ballB.mass + 1e-6))
        ballA.vel -= J * n / ballA.mass
        ballB.vel += J * n / ballB.mass
    resolve_overlap(ballA, ballB)
```

### KO via trou

```python
if point_in_arc(ball.pos, hole.arc) and ball.speed() > v_min_ko:
    register_KO(ball.team, hole.id)
    vfx_smash(hole.center, impulse=last_impulse)
    schedule_respawn_if_needed()
```

### Canon spawn

```python
def spawn_from_cannon(team, hole, rng):
    v = rng.uniform(v_min, v_max)
    ang = deg2rad(rng.normal(ang_mu, ang_sigma))
    dir_out = tangent_of_arc(hole.arc)  # direction de sortie
    vel = rotate(dir_out, ang) * v
    pos = hole.center + dir_out * (ball_radius + 2)
    return Ball(team=team, pos=pos, vel=vel)
```

---

## 11) CLI & Batch

```bash
# Une scène
python cli.py --scene scenes/circle_basic.yaml --seed 1337 \
  --out out/powerpit_circle_seed1337.mp4

# Batch 10 seeds
python batch.py --scene scenes/circle_basic.yaml --n 10 --out out/
```

---

## 12) Jalons / étapes

### M0 — Setup (0.5 j)

* [ ] Repo, venv, deps (`numpy pillow imageio[ffmpeg] pyyaml pymunk moviepy`)
* [ ] `cli.py` squelette, logger, seed RNG
* [ ] Fichier scène YAML + validation

**DoD**: lecture YAML, boucle vide → **MP4 noir** exporté.

### M1 — Physique & murs (1 j)

* [ ] Balle, intégration dt, frottement, restitution
* [ ] Murs arène (circle & stadium), bumpers
* [ ] Collisions balle-mur, balle-balle (sans knockback)

**DoD**: 2v2 qui rebondissent proprement.

### M2 — Trous & KO (0.5–1 j)

* [ ] Arcs de trous + `point_in_arc`
* [ ] KO + score + respawn grace
* [ ] Edge assist

**DoD**: KO fiables + compteur.

### M3 — Canons & fairness (0.5 j)

* [ ] Spawns par trous avec angle/vel aléatoires
* [ ] Alternance équipes + cooldown post-KO
* [ ] VFX spawn

**DoD**: respawns “propres” et lisibles.

### M4 — Buffs (1 j)

* [ ] Spawner de tokens + ramassage
* [ ] Buff Speed+/Mass+ (durée, cap, icône)
* [ ] Buff Life+ (spawn via canon le + sûr)

**DoD**: buffs visibles, effets stackables (cap).

### M5 — Render & Juice (1 j)

* [ ] Trails par team, glow simple (blur additif)
* [ ] Hitstop + screenshake + Smash VFX
* [ ] Overlays: score, timer, seed, noms équipes

**DoD**: clip 1080×1920 “satisfaisant” prêt pour réseau.

### M6 — Contenu & Batch (0.5–1 j)

* [ ] 3 arènes prêtes (circle/stadium/donut)
* [ ] 3 scènes YAML pack “S1”
* [ ] `batch.py` (N seeds → N MP4)

**DoD**: 10 clips générés automatiquement.

### M7 — Polish (continu)

* [ ] Sudden death (anneau shrink)
* [ ] Poids comeback sur buffs
* [ ] Nettoyage code + README

---

## 13) Risks & Mitigations

* **Lisibilité**: trop de particules → limiter, prioriser trails & halos.
* **Fairness**: spawn-kill → grace 1s + canon opposé.
* **RNG trop punitif**: pondérer buffs pour l’équipe en retard.
* **Perf**: éviter blur lourds; précalcul masks/paths.

---

## 14) Stretch (après MVP)

* **Arènes “cross/polygon”**, lasers rotatifs, portes battantes.
* **Modes**: 3v3, objectifs secondaires (dribble token au but), combo meter.
* **Audio sync**: KO → snare, buff → blip; beat-sync sur portes.
* **Skins/HUD personnalisables** (foot/tennis/“brainrot-safe”).

---

## 15) Définition de Done (MVP)

* Génère un MP4 vertical **1080×1920/30fps** reproductible par **seed**.
* 2v2, 3 buffs (Speed/Mass/Life), 2–3 arènes, KO + VFX smash, overlay score/timer.
* CLI & batch fonctionnels, 10 vidéos en une commande.
* README avec **exemples YAML** et commandes.

---

