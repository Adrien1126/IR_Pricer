import QuantLib as ql
import datetime
from datetime import date
from pricer.utils.mappings import DAY_COUNT_MAP, CALENDAR_MAP, BUSINESS_CONVENTION_MAP

def year_fraction(start: date, end: date, convention: str = "Actual360") -> float:
    """
    Calcule la fraction d'année entre deux dates selon une convention de day count.
    
    Args:
        start (date): Date de début.
        end (date): Date de fin.
        convention (str): Nom de la convention de calcul (par défaut "Actual360").
    
    Returns:
        float: Fraction d'année entre start et end selon la convention.
    
    Raises:
        ValueError: Si la convention n'est pas supportée.
    """
    # Récupère l'objet QuantLib correspondant à la convention
    dc = DAY_COUNT_MAP.get(convention)
    if dc is None:
        raise ValueError(f"Unsupported day count convention: {convention}")
    
    # Convertit les dates Python en dates QuantLib
    ql_start = ql.Date(start.day, start.month, start.year)
    ql_end = ql.Date(end.day, end.month, end.year)
    
    # Calcule la fraction d'année via QuantLib
    return dc.yearFraction(ql_start, ql_end)


def advance_date(start: date, tenor: str, calendar: str = "TARGET", convention: str = "ModifiedFollowing") -> date:
    """
    Avance une date selon un tenor, un calendrier et une convention de business day.
    
    Args:
        start (date): Date de départ.
        tenor (str): Durée à ajouter (ex: "3M" pour 3 mois).
        calendar (str): Calendrier pour considérer les jours ouvrés (défaut "TARGET").
        convention (str): Convention pour ajuster la date si elle tombe un jour non ouvré (défaut "ModifiedFollowing").
    
    Returns:
        date: Date ajustée après avance.
    
    Raises:
        ValueError: Si le calendrier ou la convention ne sont pas supportés.
    """
    # Récupère le calendrier QuantLib
    ql_cal = CALENDAR_MAP.get(calendar)
    if ql_cal is None:
        raise ValueError(f"Unsupported calendar: {calendar}")
    
    # Récupère la convention de business day
    conv = BUSINESS_CONVENTION_MAP.get(convention)
    if conv is None:
        raise ValueError(f"Unsupported business day convention: {convention}")
    
    # Convertit la date de départ en QuantLib
    ql_start = ql.Date(start.day, start.month, start.year)
    
    # Avance la date selon le tenor et applique la convention d'ajustement
    ql_end = ql_cal.advance(ql_start, ql.Period(tenor), conv)
    
    # Retourne une date Python classique
    return date(ql_end.year(), ql_end.month(), ql_end.dayOfMonth())


def to_pydate(d) -> datetime.date:
    """Convertit un objet QuantLib.Date ou datetime.date en datetime.date"""
    if isinstance(d, ql.Date):
        return datetime.date(d.year(), d.month(), d.dayOfMonth())
    elif isinstance(d, datetime.date):
        return d
    elif isinstance(d, datetime.datetime):  # tolérance
        return d.date()
    else:
        raise TypeError(f"Type de date non supporté : {type(d)}")