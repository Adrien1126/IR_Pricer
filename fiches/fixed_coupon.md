# Fiche technique — Coupon à taux fixe (FixedCoupon)

## 1. Contexte général  
Un coupon fixe correspond à un paiement d’intérêt connu à l’avance, basé sur un taux fixe appliqué à un montant notionnel, pour une période donnée.

## 2. Concepts financiers clés  
- **Notional** : montant sur lequel les intérêts sont calculés.  
- **Taux fixe** : taux d’intérêt constant appliqué sur la période d’accrual.  
- **Période d’accrual** : intervalle entre `start_date` et `end_date` où les intérêts s’accumulent.  
- **Date de paiement** : date où l’intérêt est versé.  
- **Convention day count** : règle pour calculer la fraction d’année entre deux dates (ex : Actual/360).  
- **Calendrier** : calendrier des jours ouvrés utilisé pour ajuster les dates.

## 3. Fonctionnalités développées  
- Validation des données en entrée via un modèle Pydantic (`FixedCouponModel`) pour garantir la cohérence.  
- Classe métier `FixedCoupon` qui hérite de `BaseCoupon` et implémente le calcul du montant du coupon fixe.  
- Conversion automatique des dates et conventions en objets QuantLib pour utiliser leurs méthodes financières.

## 4. Exemple d’utilisation

```python
from datetime import date
model = FixedCouponModel(
    start_date=date(2025, 1, 1),
    end_date=date(2025, 7, 1),
    payment_date=date(2025, 7, 3),
    notional=1_000_000,
    fixed_rate=0.05,
    calendar="TARGET",
    day_count="Actual360"
)
coupon = FixedCoupon(model)
print(coupon)
print(f"Montant du coupon: {coupon.amount():.2f}")
```

## 5. Glossaire rapide

**Coupon fixe** : paiement d’intérêt basé sur un taux constant.

**Notional** : montant de référence pour calculer les intérêts.

**Day count** : méthode pour calculer la fraction d’année entre deux dates.

**Calendrier** : jours ouvrés utilisés pour ajuster les dates.