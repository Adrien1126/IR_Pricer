# Fiche technique — Jambe à taux variable (FloatingLeg)

## 1. Contexte général

Une jambe à taux variable (FloatingLeg) est une série de paiements d’intérêts où le taux varie selon un index financier (ex : EURIBOR 3 mois), auquel peut s’ajouter un spread.

## 2. Concepts financiers clés

* **Notional** : montant principal servant au calcul des intérêts.
* **Index** : taux de référence variable (ex : EURIBOR 3M).
* **Spread** : marge ajoutée au taux de l’index.
* **Fixing lag** : délai entre la date à laquelle le taux est observé (fixing) et la date d’application.
* **Payment lag** : délai entre la fin de la période d’intérêt et la date de paiement.
* **Schedule** : calendrier des périodes d’intérêt.
* **Day count & Business convention** : conventions pour calculer les intérêts et ajuster les dates.

## 3. Fonctionnalités développées

* Modèle Pydantic (`FloatingLegModel`) pour valider les données d’entrée.
* Génération du calendrier de paiement avec QuantLib.
* Création des coupons variables (`FloatingCoupon`) utilisant l’index et le spread.
* Gestion du fixing lag pour déterminer la date à laquelle le taux est observé.
* Calcul dynamique du montant du coupon selon le taux index + spread.

## 4. Exemple d’utilisation

```python
from datetime import date
import QuantLib as ql

# Setup QuantLib evaluation date
ql.Settings.instance().evaluationDate = ql.Date(31, 1, 2025)

# Courbe plate à 3%
curve = ql.FlatForward(ql.Date(31, 1, 2025), 0.03, ql.Actual360())
index = ql.Euribor3M(ql.YieldTermStructureHandle(curve))

model = FloatingLegModel(
    start_date=date(2025, 1, 31),
    end_date=date(2025, 6, 30),
    notional=1_000_000,
    payment_frequency="1M",
    index_name="EURIBOR3M",
    spread=0.0025,
    calendar="TARGET",
    day_count="Actual360",
    business_convention="ModifiedFollowing",
    fixing_lag=2,
    payment_lag=2,
)

floating_leg = FloatingLeg(model, index)
coupons = floating_leg.build_leg()

for i, coupon in enumerate(coupons, 1):
    print(f"Coupon {i}: {coupon}")
    print(f"Montant = {coupon.amount():.2f}")
```

## 5. Glossaire rapide

* **FloatingLeg** : ensemble de paiements à taux variable indexés.
* **Index** : taux financier variable (ex : EURIBOR).
* **Spread** : marge ajoutée au taux index.
* **Fixing lag** : délai entre observation du taux et application.
* **Payment lag** : délai entre fin période et paiement effectif.
* **Schedule** : calendrier des paiements et périodes d’intérêt.
