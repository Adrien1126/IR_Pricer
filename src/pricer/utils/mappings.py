import QuantLib as ql

# --- Calendriers supportés ---
# Cette partie définit un dictionnaire qui associe des noms de calendriers à des objets
# QuantLib correspondants. Un calendrier sert à définir les jours ouvrés (jours de marché)
# pour la gestion des dates dans les instruments financiers.
# Par exemple, TARGET correspond au calendrier des jours ouvrés européens,
# UnitedStates à celui des bourses américaines, etc.
CALENDAR_MAP = {
    "TARGET": ql.TARGET(),
    "UnitedStates": ql.UnitedStates(ql.UnitedStates.NYSE),
    "NullCalendar": ql.NullCalendar(),  # calendrier sans jours fériés (tous les jours sont ouvrés)
}

# --- Conventions de day count supportées ---
# Ce dictionnaire mappe des noms de conventions comptables de jours ("day count") à des objets QuantLib.
# Une convention de day count est une règle qui définit comment compter les jours entre deux dates
# pour calculer des intérêts. Par exemple, Actual360 compte les jours réels sur une base 360 jours.
DAY_COUNT_MAP = {
    "Actual360": ql.Actual360(),
    "Thirty360": ql.Thirty360(ql.Thirty360.BondBasis),     # US Bond Basis : chaque mois compte 30 jours, chaque année 360 jours
    "Thirty360E": ql.Thirty360(ql.Thirty360.European),     # Variante européenne de la règle 30/360
    "Actual365Fixed": ql.Actual365Fixed(),                 # Compte les jours réels sur une base fixe de 365 jours par an
}

# --- Conventions de business day ---
# Ces conventions servent à ajuster une date qui tomberait un jour non ouvré.
# Par exemple, si un paiement tombe un dimanche, on applique une règle pour reporter la date.
BUSINESS_CONVENTION_MAP = {
    "Following": ql.Following,           # Date est repoussée au jour ouvré suivant
    "ModifiedFollowing": ql.ModifiedFollowing,  # Comme Following, sauf si ça dépasse le mois, alors on recule
    "Preceding": ql.Preceding,           # Date est avancée au jour ouvré précédent
    "Unadjusted": ql.Unadjusted,         # Pas d'ajustement, on garde la date telle quelle
}

# --- Fréquences de paiement ---
# Fréquences des paiements (coupon ou autres flux) exprimées en mois.
# Par exemple, 3M signifie paiement trimestriel, 6M semestriel, 12M annuel.
PAYMENT_FREQUENCY_MAP = {
    "1M": ql.Period(1, ql.Months),
    "3M": ql.Period(3, ql.Months),
    "6M": ql.Period(6, ql.Months),
    "12M": ql.Period(12, ql.Months),
}

