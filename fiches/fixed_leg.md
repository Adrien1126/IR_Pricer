# Fiche technique — Jambe à taux fixe (FixedLeg)

## 1. Contexte général

Une jambe à taux fixe (FixedLeg) est une série de paiements d’intérêts périodiques où le taux est connu et constant pour toute la durée de la jambe.

## 2. Concepts financiers clés

* **Notional** : montant principal sur lequel les intérêts sont calculés.
* **Taux fixe** : taux d’intérêt constant appliqué à chaque période.
* **Schedule (calendrier)** : liste des dates qui définissent les périodes d’intérêt (du début à la fin).
* **Date de paiement** : date à laquelle l’intérêt de chaque période est payé, souvent ajustée selon des règles de jours ouvrés.
* **Day count convention** : règle pour calculer la fraction d’année entre deux dates (ex : Actual/360).
* **Business convention** : méthode pour ajuster les dates qui tombent un jour non ouvré.

## 3. Fonctionnalités développées

* Modèle Pydantic (`FixedLegModel`) pour valider toutes les données d’entrée avant création.
* Construction du calendrier de paiement (schedule) avec QuantLib en fonction des paramètres (fréquence, calendrier, conventions).
* Création des coupons fixes (`FixedCoupon`) pour chaque période selon le calendrier.
* Calcul du montant de chaque coupon basé sur le taux fixe, le notional, et la période d’accrual.

## 4. Exemple d’utilisation

```python
from datetime import date
model = FixedLegModel(
    start_date=date(2025, 1, 31),
    end_date=date(2025, 6, 30),
    notional=1_000_000,
    payment_frequency="1M",
    fixed_rate=0.05,
    calendar="TARGET",
    day_count="Actual360",
    business_convention="ModifiedFollowing",
    payment_lag=0,
)
fixed_leg = FixedLeg(model)
coupons = fixed_leg.build_leg()

for i, coupon in enumerate(coupons, 1):
    print(f"Coupon {i}: {coupon}")
    print(f"Montant = {coupon.amount():.2f}")
```

## 5. Glossaire rapide

* **FixedLeg** : ensemble de paiements à taux constant.
* **Notional** : montant principal servant de base au calcul des intérêts.
* **Payment frequency** : intervalle entre deux paiements (ex: 1M = mensuel).
* **Schedule** : dates de début et fin des périodes d’intérêt.
* **Business convention** : règle d’ajustement des dates non ouvrées.
