# IR_Pricer

Petit pricer de taux d’intérêt (Interest Rate) basé sur QuantLib. Projet en tout début (WIP) qui va fortement évoluer.

- Langage/stack: Python 3.12, QuantLib, Pydantic v2, PyTest
- Portée actuelle: modélisation de coupons/legs fixes et flottants, génération de schedule, montants de coupons
- À venir: valorisation (NPV), calibration/chargement de courbes, solveurs (par rate), plus de conventions, plus de tests

## Architecture du projet

```
IR_Pricer/
├─ hello_pricer.py                # Script d’accueil
├─ requirements.txt               # Dépendances
├─ src/
│  └─ pricer/
│     ├─ instruments/
│     │  ├─ coupon.py            # BaseCoupon (abstraite)
│     │  ├─ fixed_coupon.py      # Coupon fixe (+ modèle Pydantic)
│     │  ├─ floating_coupon.py   # Coupon flottant (+ modèle Pydantic)
│     │  ├─ leg.py               # BaseLeg (schedule QuantLib)
│     │  ├─ fixed_leg.py         # Jambe fixe (assemble des FixedCoupon)
│     │  └─ floating_leg.py      # Jambe flottante (assemble des FloatingCoupon)
│     └─ utils/
│        └─ mappings.py          # Mappings str -> objets QuantLib (calendrier, day count, conventions, fréquences)
└─ tests/
   ├─ test_fixed_coupon.py        # Tests sur FixedCoupon/validation
   └─ test_fixed_leg.py           # Tests sur FixedLeg/validation/construction
```

Notes techniques:
- Layout en « src/ »: il faut exposer le package `pricer` via `PYTHONPATH=src` lors des exécutions.
- Les démos utilisent des courbes plates (FlatForward) pour illustrer le fonctionnement.

## Détail des scripts dans `src/`

- `src/pricer/__init__.py`
  - Marqueur de package Python. Peut exposer des symboles publics du package `pricer` (actuellement minimal).

- `src/pricer/instruments/coupon.py`
  - Base abstraite `BaseCoupon` (dates d’accrual, date de paiement, notionnel, calendrier).
  - Méthode abstraite `amount()` implémentée par les coupons concrets.

- `src/pricer/instruments/fixed_coupon.py`
  - `FixedCouponModel` (Pydantic) valide les entrées: dates cohérentes, notionnel > 0, taux ∈ [0,1], mapping calendrier/day count.
  - `FixedCoupon`: calcule le montant = Notional × FixedRate × YearFraction.
  - Module exécutable: démo rapide en `python -m pricer.instruments.fixed_coupon`.

- `src/pricer/instruments/floating_coupon.py`
  - `FloatingCouponModel` (Pydantic): champs pour index, spread, fixing lag, conventions, validations.
  - `FloatingCoupon`: récupère un fixing s’il existe sinon un taux forward via la courbe de l’index (`forwardingTermStructure`).
  - Utilise un `ql.IborIndex` passé au constructeur (ex: `ql.Euribor3M`).
  - Module exécutable: démo avec courbe plate.

- `src/pricer/instruments/leg.py`
  - `BaseLeg`: base pour les jambes (start/end, notional, calendrier, fréquence, day count, business convention, payment lag).
  - Génère un `ql.Schedule` et expose `generate_schedule()`; laisse `build_leg()` aux classes filles.

- `src/pricer/instruments/fixed_leg.py`
  - `FixedLegModel` (Pydantic): valide notional, taux, calendrier, day count, conventions, fréquence, cohérence des dates.
  - `FixedLeg`: construit des `FixedCoupon` à partir du schedule et applique le `payment_lag` et la convention de business day.
  - Module exécutable: imprime les coupons et leurs montants.

- `src/pricer/instruments/floating_leg.py`
  - `FloatingLegModel` (Pydantic): valide les paramètres d’une jambe flottante (fréquence, calendrier, day count, conventions, lags).
  - `FloatingLeg`: nécessite un index Ibor; construit des `FloatingCoupon` pour chaque période du schedule.
  - Module exécutable: imprime les coupons et montants en utilisant une courbe plate.

- `src/pricer/instruments/swap.py`
  - `SwapModel`: décrit un swap vanilla (trade_date, end_date, spot_lag, notional, fixed_rate, fréquences, spread, conventions par jambe).
  - `Swap`: calcule `value_date` (trade_date + spot_lag selon calendrier), construit une jambe fixe et une jambe flottante, sans NPV pour l’instant.
  - Module exécutable: affiche les coupons des deux jambes.

- `src/pricer/utils/mappings.py`
  - Dictionnaires de mapping simples: calendriers (`TARGET`, `UnitedStates`, `NullCalendar`), day counts (`Actual360`, `Thirty360`, ...),
    conventions de business day (`Following`, `ModifiedFollowing`, ...), fréquences de paiement (`1M`, `3M`, `6M`, `12M`).

## Installation (Linux, bash)

1) Créer/activer un environnement virtuel et installer les dépendances:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2) Facultatif mais pratique: exporter `PYTHONPATH` pour cette session terminal

```bash
export PYTHONPATH=src
```

Sans cet export, préfixez vos commandes avec `PYTHONPATH=src`.

## Utilisation en console

Scripts/démos existants:
- Accueil:
  ```bash
  python hello_pricer.py
  ```
- Coupon fixe:
  ```bash
  PYTHONPATH=src python -m pricer.instruments.fixed_coupon
  ```
- Jambe fixe:
  ```bash
  PYTHONPATH=src python -m pricer.instruments.fixed_leg
  ```
- Jambe flottante:
  ```bash
  PYTHONPATH=src python -m pricer.instruments.floating_leg
  ```
- Swap vanilla (1 jambe fixe + 1 jambe flottante):
  ```bash
  PYTHONPATH=src python -m pricer.instruments.swap
  ```

## Lancer les tests

```bash
PYTHONPATH=src pytest -q
```

Résultat actuel attendu: « 9 passed, 3 warnings » (peut évoluer).

## Concepts clés (actuels)

- Coupon fixe (`FixedCoupon`): montant = Notional × FixedRate × YearFraction(day count)
- Coupon flottant (`FloatingCoupon`): montant = Notional × (Index + Spread) × YearFraction
  - Le taux provient d’un fixing si dispo, sinon de la courbe (forwardingTermStructure)
- Leg (`BaseLeg`): centralise la génération du schedule (QuantLib `Schedule`), conventions business day et fréquence
- Validation Pydantic: sécurité d’entrée via modèles `*Model`

## Limitations connues (WIP)

- Pas (encore) de valorisation (NPV/discounting), uniquement calcul des montants de coupons
- Courbes: exemples avec FlatForward; pas de construction/calibration avancée
- Mapping de conventions limité (calendriers/day count/frequences)
- Peu de tests sur la partie flottante/swap (à étoffer)

## Roadmap (indicative)

- Pricing: NPV des legs et des swaps (courbe de discount, choix de compounding)
- Solveurs: par rate, break-even spread, DV01
- Courbes: loaders (CSV, APIs), bootstrapping, multi-curve (OIS/forward)
- Conventions: périodes irrégulières, stub, end-of-month, accrual vs payment calendars
- Qualité: plus de tests, type hints stricts, CI, couverture
- Ergonomie: CLI simple (ex: `python -m pricer ...`), exemples réplicables

## Contribution

- Ouvert aux suggestions/PRs. Le projet est jeune: l’API peut changer.
- Style conseillé: code typé, tests PyTest, docstrings courts et clairs.