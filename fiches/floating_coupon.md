# Fiche technique — Coupon à taux variable (FloatingCoupon)

## 1. Contexte général  
Un coupon à taux variable est un paiement d’intérêt dont le taux est indexé sur un indice de référence (ex : EURIBOR 3M). Ce taux peut varier selon les conditions de marché.

## 2. Concepts financiers clés  
- **Notional** : montant sur lequel les intérêts sont calculés.  
- **Taux indexé** : taux observé sur un index (ex : EURIBOR 3M) à une date de fixing.  
- **Spread** : écart fixe ajouté au taux indexé pour ajuster le coupon.  
- **Période d’accrual** : intervalle entre `start_date` et `end_date` où les intérêts courent.  
- **Date de fixing** : date à laquelle le taux indexé est observé, souvent avec un décalage (fixing lag) avant le début de la période.  
- **Convention day count** : règle pour calculer la fraction d’année entre deux dates.  
- **Calendrier** : calendrier financier utilisé pour ajuster les dates selon les jours ouvrés.  
- **Convention business day** : règle d’ajustement des dates tombant un jour non ouvré.

## 3. Fonctionnalités développées  
- Validation des données via Pydantic (`FloatingCouponModel`) pour garantir cohérence et support des conventions.  
- Classe métier `FloatingCoupon` hérite de `BaseCoupon` et implémente :  
  - La détermination du taux indexé : soit récupération d’un fixing historique, soit calcul forward via la courbe associée.  
  - Le calcul du montant du coupon flottant avec spread.

## 4. Exemple d’utilisation

```python
from datetime import date
model = FloatingCouponModel(
    start_date=date(2025, 1, 31),
    end_date=date(2025, 4, 30),
    payment_date=date(2025, 5, 2),
    notional=1_000_000,
    spread=0.0025,
    index_name="EURIBOR3M",
    calendar="TARGET",
    day_count="Actual360",
    fixing_lag=2,
    convention="ModifiedFollowing"
)

# index est un objet QuantLib IborIndex initialisé avec une courbe
coupon = FloatingCoupon(model, index)
print(coupon)
print(f"Montant du coupon : {coupon.amount():.2f} EUR")
```

## 5. Glossaire rapide

**Coupon flottant** : paiement d’intérêt basé sur un taux variable indexé.

**Fixing** : observation du taux sur l’index à une date donnée.

**Spread** : marge ajoutée au taux indexé.

**Fixing lag** : délai en jours entre la date de fixing et le début de la période.

**Business day convention** : règle pour ajuster les dates sur des jours ouvrés.