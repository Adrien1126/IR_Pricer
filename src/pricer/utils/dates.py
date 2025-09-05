import QuantLib as ql
from datetime import date
from pricer.utils.mappings import DAY_COUNT_MAP, CALENDAR_MAP, BUSINESS_CONVENTION_MAP

def year_fraction(start: date, end: date, convention: str = "Actual360") -> float:
    dc = DAY_COUNT_MAP.get(convention)
    if dc is None:
        raise ValueError(f"Unsupported day count convention: {convention}")
    ql_start = ql.Date(start.day, start.month, start.year)
    ql_end = ql.Date(end.day, end.month, end.year)
    return dc.yearFraction(ql_start, ql_end)

def advance_date(start: date, tenor: str, calendar: str = "TARGET", convention: str = "ModifiedFollowing") -> date:
    ql_cal = CALENDAR_MAP.get(calendar)
    if ql_cal is None:
        raise ValueError(f"Unsupported calendar: {calendar}")
    conv = BUSINESS_CONVENTION_MAP.get(convention)
    if conv is None:
        raise ValueError(f"Unsupported business day convention: {convention}")
    ql_start = ql.Date(start.day, start.month, start.year)
    ql_end = ql_cal.advance(ql_start, ql.Period(tenor), conv)
    return date(ql_end.year(), ql_end.month(), ql_end.dayOfMonth())
