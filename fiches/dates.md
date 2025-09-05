# Fiche technique — Calcul de fractions d’années et avancée de dates

## 1. Contexte général  
Dans le cadre du pricer, il est souvent nécessaire de calculer la durée entre deux dates exprimée en fraction d’année, ainsi que d’avancer une date en tenant compte des jours ouvrés et des règles financières.

## 2. Concepts financiers clés  
- **Fraction d’année (year fraction)** : La durée entre deux dates exprimée en nombre d’années selon une règle spécifique (convention de day count).  
- **Tenor** : Durée exprimée en mois ou années (exemple "3M" = 3 mois) pour avancer une date.  
- **Calendrier financier** : Liste des jours ouvrés pour un marché donné (exemple TARGET pour l’Europe).  
- **Convention de business day** : Règle d’ajustement des dates si elles tombent un jour non ouvré (exemple ModifiedFollowing).

## 3. Fonctionnalités développées  
- `year_fraction(start, end, convention)` : calcule la fraction d’année entre deux dates selon une convention donnée.  
- `advance_date(start, tenor, calendar, convention)` : calcule la date obtenue en avançant la date de départ selon un tenor, un calendrier et une convention de business day.

Ces fonctions sont des **wrappers** autour de QuantLib, pour faciliter leur réutilisation et un éventuel remplacement futur de QuantLib.

## 4. Exemple d’utilisation

Calculer la fraction d’année entre le 1er janvier 2023 et le 1er juillet 2023 avec la convention Actual360 :

```python
from datetime import date
frac = year_fraction(date(2023, 1, 1), date(2023, 7, 1), "Actual360")
print(frac)  # Ex: environ 0.5
```

Avancer la date du 1er janvier 2023 de 3 mois en tenant compte du calendrier TARGET et de la convention ModifiedFollowing :

```python
new_date = advance_date(date(2023, 1, 1), "3M", calendar="TARGET", convention="ModifiedFollowing")
print(new_date)  # Ex: 2023-04-03 (si 1er avril est un week-end)
```

## 5. Glossaire rapide

**Fraction d’année** : Mesure du temps entre deux dates utilisée pour calculer des intérêts.

**Tenor** : Durée pour avancer une date.

**Calendrier financier** : Définit les jours où les marchés sont ouverts.

**Convention de business day** : Règle pour ajuster les dates qui tombent hors jours ouvrés.