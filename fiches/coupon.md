# Fiche technique — Classe abstraite BaseCoupon

## 1. Contexte général  
Le coupon est une composante clé des instruments de taux : c’est le paiement d’intérêt que reçoit le détenteur.  
Cette classe abstraite modélise un coupon financier générique, en gérant les dates importantes et le montant notionnel.

## 2. Concepts financiers clés  
- **Coupon** : paiement périodique d’intérêt lié à un montant notionnel.  
- **Période d’accrual** : intervalle entre `start_date` et `end_date` pendant lequel les intérêts s’accumulent.  
- **Date de paiement** : date à laquelle l’intérêt est effectivement payé. Souvent après la fin de la période d’accrual.  
- **Notional** : montant de référence sur lequel les intérêts sont calculés.  
- **Calendrier financier** : calendrier des jours ouvrés utilisé pour ajuster les dates.

## 3. Fonctionnalités développées  
- Classe abstraite qui sert de base à différents types de coupons (fixes, variables...).  
- Conversion des dates Python en dates QuantLib pour bénéficier des outils de gestion financière.  
- Méthode abstraite `amount()` à définir dans les sous-classes, pour calculer le montant du coupon.

## 4. Exemple d’utilisation  
La classe seule ne s’utilise pas directement (méthode abstraite), mais une classe fille pourrait être :

```python
class FixedCoupon(BaseCoupon):
    def __init__(self, fixed_rate: float, **kwargs):
        super().__init__(**kwargs)
        self.fixed_rate = fixed_rate

    def amount(self) -> float:
        # Exemple simple : montant = notional * taux fixe * fraction d'année (calculée ailleurs)
        # Ici, on retourne juste un exemple fixe
        return self.notional * self.fixed_rate
```

## 5. Glossaire rapide

**Coupon** : paiement d’intérêt périodique.

**Période d’accrual** : période pendant laquelle les intérêts s’accumulent.

**Notional** : montant de référence pour les calculs d’intérêts.

**Classe abstraite** : classe qui définit une interface, mais ne peut être instanciée directement.