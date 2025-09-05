# Fiche technique — Mappings des paramètres financiers

## 1. Contexte général  
Dans le cadre du pricer d'instruments de taux, il est nécessaire de manipuler des dates, des règles de calcul d'intérêts et des fréquences de paiement. Ces règles varient selon le marché, le type d’instrument, et les conventions financières.

## 2. Concepts financiers clés  
- **Calendrier financier** : C’est une liste des jours où la bourse ou le marché fonctionne (jours ouvrés). Par exemple, en Europe, le marché est fermé certains jours fériés.  
- **Convention de day count** : Règle qui indique comment compter les jours entre deux dates pour calculer les intérêts (ex. Actual/360 signifie qu’on compte les jours réels mais on divise par 360).  
- **Convention de business day** : Règle qui ajuste une date si elle tombe un jour non ouvré (ex. un dimanche).  
- **Fréquence de paiement** : Intervalle entre chaque paiement d’intérêt (ex. tous les 3 mois).

## 3. Fonctionnalités développées  
Ce fichier crée des dictionnaires qui permettent de traduire des noms simples (ex. "TARGET", "Actual360") en objets QuantLib, qui sont utilisés dans les calculs financiers. Cela rend le code plus lisible et adaptable.

## 4. Exemple d’utilisation  
Si on veut créer un calendrier pour les jours ouvrés en Europe, on utilisera :  
```python
calendar = CALENDAR_MAP["TARGET"]
```
Si on veut appliquer la règle de décompte Actual/360 :
```python
day_count = DAY_COUNT_MAP["Actual360"]
```

## 5. Glossaire rapide

**Calendrier** : Liste des jours où les transactions financières sont possibles.

**Day count** : Façon de compter les jours pour calculer les intérêts.

**Business day convention** : Règle pour ajuster une date non ouvrée.

**Fréquence** : Intervalle entre paiements.