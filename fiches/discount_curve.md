# Fiche technique — Discount Curve

## 1. Contexte général

Une **courbe de discount** (ou courbe d’actualisation) donne, pour chaque date future, un **facteur d’actualisation** permettant de convertir un montant d’argent futur en sa valeur actuelle.

## 2. Concepts financiers clés

* **Facteur d’actualisation (Discount Factor)** : coefficient entre 0 et 1 qui permet de transformer un montant reçu à une date future en sa valeur équivalente aujourd’hui.
* **Piliers (pillars)** : dates pour lesquelles on connaît les facteurs d’actualisation observés sur le marché.
* **Interpolation** : méthode pour estimer les facteurs d’actualisation à des dates intermédiaires entre les piliers connus.
* **Convention day count** : règle qui permet de mesurer la fraction d’année entre deux dates (ex : Actual/360).
* **Calendrier** : ensemble des jours ouvrés pour ajuster les dates selon les règles de marché.

## 3. Fonctionnalités développées

* Validation rigoureuse des données d’entrée via Pydantic (`DiscountCurveModel`).
* Construction automatique de la courbe à partir des piliers fournis.
* Interpolation des facteurs selon différents modes (linéaire, cubique) et sur différentes quantités (facteur direct, logarithme, taux zéro).
* Gestion possible de l’extrapolation au-delà des piliers fournis.
* Calcul du facteur d’actualisation pour n’importe quelle date cible.

## 4. Interprétation économique et financière du facteur d’actualisation

### Qu’est-ce qu’un facteur d’actualisation ?

C’est un nombre qui exprime la **valeur actuelle d’1€ à recevoir dans le futur**. Il reflète l’idée que **l’argent vaut plus aujourd’hui que demain**.

### Pourquoi le facteur est-il toujours entre 0 et 1 ?

* Si on attend un paiement futur, sa valeur d’aujourd’hui est inférieure ou égale à ce montant, car:

  * L’argent peut être investi pour générer un gain (coût d’opportunité).
  * Il y a un risque que ce paiement ne soit pas reçu (risque crédit).
  * Il y a une préférence naturelle pour disposer de liquidités immédiatement.

### Exemple simple :

* Facteur = 1.0 à 0 jour (aujourd’hui) : 1€ vaut 1€ maintenant.
* Facteur = 0.95 à 6 mois : 1€ reçu dans 6 mois vaut 0,95€ aujourd’hui.
* Facteur = 0.90 à 2 ans : 1€ reçu dans 2 ans vaut 0,90€ aujourd’hui.

### À quoi sert-il ?

* **Évaluer des flux futurs** : valoriser un paiement futur en l’actualisant.
* **Construire des prix d’actifs financiers** : obligations, prêts, swaps, etc.
* **Comparer des montants à des dates différentes** : savoir combien vaut un euro à date A par rapport à un euro à date B.

## 5. Exemple d’utilisation

```python
from datetime import date
from pricer.instruments.discount_curve import DiscountCurveModel, DiscountCurve
from pricer.utils.dates import advance_date

today = date.today()

pillars = [
    ("0D", 1.0),
    ("6M", 0.98),
    ("1Y", 0.95),
    ("18M", 0.93),
    ("2Y", 0.90),
]

model = DiscountCurveModel(
    value_date=today,
    pillars=pillars,
    interp_method="linear",
    interpolation_on="log_discount",
    allow_extrapolation=True,
    day_count="Actual360",
    calendar="TARGET",
    business_day_convention="ModifiedFollowing",
    currency="EUR",
    curve_id="EUR_EONIA_DISC"
)

curve = DiscountCurve.from_model(model)
target_date = advance_date(today, "9M", calendar="TARGET")
df = curve.discount_factor(target_date)

print(f"[{model.curve_id}] DF({target_date}) = {df:.6f}")
```
