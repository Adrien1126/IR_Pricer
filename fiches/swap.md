# Fiche technique — Swap vanilla (Swap)

## 1. Contexte général

Un swap vanilla est un contrat financier où deux parties échangent des flux d’intérêts :

* Une jambe à taux fixe (Fixed Leg)
* Une jambe à taux variable (Floating Leg)

L’échange porte sur un même montant notionnel, durant une période donnée.

## 2. Concepts financiers clés

* **Trade date** : date de signature du contrat.
* **Value date** : date de départ effective du swap, généralement le trade date + spot lag (délai standard).
* **Notional** : montant principal sur lequel les intérêts sont calculés.
* **Fixed leg** : série de paiements à taux fixe sur la durée du swap.
* **Floating leg** : série de paiements à taux variable indexés sur un taux de référence (ex : EURIBOR).
* **Spread** : marge ajoutée au taux variable (floating leg).
* **Fréquences de paiement** : intervalles entre paiements fixes et variables (ex : mensuel, trimestriel).
* **Calendrier & conventions** : règles pour ajuster les dates de paiement selon les jours ouvrés.

## 3. Fonctionnalités développées

* Modèle Pydantic (`SwapModel`) pour valider les paramètres du swap (dates, notionnel, taux, fréquences, conventions).
* Calcul automatique de la **value date** à partir de la trade date et du spot lag.
* Construction d’une jambe fixe (`FixedLeg`) et d’une jambe variable (`FloatingLeg`) avec leurs propres paramètres.
* Utilisation de QuantLib pour gérer les calendriers, les conventions, et le calcul des dates de paiement.
* Création des coupons pour chaque jambe, permettant le calcul des montants des intérêts à payer.

## 4. Exemple d’utilisation

```python
from datetime import date
import QuantLib as ql

trade_date = date(2025, 1, 31)
end_date = date(2026, 1, 31)

ql_date = ql.Date(trade_date.day, trade_date.month, trade_date.year)
ql.Settings.instance().evaluationDate = ql_date

# Courbe plate pour taux d'intérêt 3%
curve = ql.FlatForward(ql_date, 0.03, ql.Actual360())
index_handle = ql.YieldTermStructureHandle(curve)
euribor_index = ql.Euribor3M(index_handle)

swap_model = SwapModel(
    trade_date=trade_date,
    end_date=end_date,
    notional=1_000_000,
    fixed_rate=0.05,
    fixed_frequency="1M",
    floating_frequency="1M",
    spread=0.0025,
    floating_payment_lag=2,
)

swap = Swap(swap_model, floating_index=euribor_index)

print("Fixed leg coupons :")
for i, c in enumerate(swap.fixed_leg.coupons, 1):
    print(f"Coupon {i}: {c} - Montant = {c.amount():.2f}")

print("\nFloating leg coupons :")
for i, c in enumerate(swap.floating_leg.coupons, 1):
    print(f"Coupon {i}: {c} - Montant = {c.amount():.2f}")
```

## 5. Glossaire rapide

* **Swap** : échange de flux financiers entre une jambe fixe et une jambe variable.
* **Trade date** : date de signature.
* **Value date** : date de départ du calcul des intérêts (trade date + spot lag).
* **Notional** : montant de base pour les calculs d’intérêts.
* **Fixed leg** : série de paiements à taux fixe.
* **Floating leg** : série de paiements à taux variable indexé.
* **Spread** : marge ajoutée au taux variable.
* **Spot lag** : délai standard entre trade date et value date.
* **Calendrier** : jours ouvrés pour ajustement des dates.
* **Business convention** : règle pour gérer les dates non ouvrées.
