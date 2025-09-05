import QuantLib as ql
from datetime import date

def year_fraction(start: date, end: date, convention: str = "Actual360") -> float:
    ql_start = ql.Date(start.day, start.month, start.year)
    ql_end = ql.Date(end.day, end.month, end.year)

    # Exemple : Actual/360, Actual/365, Thirty360, etc.
    day_counter = {
        "Actual360": ql.Actual360(),
        "Actual365": ql.Actual365Fixed(),
        "Thirty360": ql.Thirty360(ql.Thirty360.BondBasis),
    }.get(convention)

    if day_counter is None:
        raise ValueError(f"Unsupported convention: {convention}")

    return day_counter.yearFraction(ql_start, ql_end)
