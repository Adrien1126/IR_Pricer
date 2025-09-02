# src/pricer/utils/mappings.py

import QuantLib as ql

# --- Calendriers supportés ---
CALENDAR_MAP = {
    "TARGET": ql.TARGET(),
    "UnitedStates": ql.UnitedStates(ql.UnitedStates.NYSE),
    "NullCalendar": ql.NullCalendar(),
}

# --- Conventions de day count supportées ---
DAY_COUNT_MAP = {
    "Actual360": ql.Actual360(),
    "Thirty360": ql.Thirty360(ql.Thirty360.BondBasis),     # US Bond Basis
    "Thirty360E": ql.Thirty360(ql.Thirty360.European),     # European
    "Actual365Fixed": ql.Actual365Fixed(),
}

# --- Conventions de business day ---
BUSINESS_CONVENTION_MAP = {
    "Following": ql.Following,
    "ModifiedFollowing": ql.ModifiedFollowing,
    "Preceding": ql.Preceding,
    "Unadjusted": ql.Unadjusted,
}

# --- Fréquences de paiement ---
PAYMENT_FREQUENCY_MAP = {
    "1M": ql.Period(1, ql.Months),
    "3M": ql.Period(3, ql.Months),
    "6M": ql.Period(6, ql.Months),
    "12M": ql.Period(12, ql.Months),
}