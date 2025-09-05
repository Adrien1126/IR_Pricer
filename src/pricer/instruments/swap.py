# src/pricer/instruments/swap.py

from datetime import date, timedelta
from pydantic import BaseModel, model_validator
from pricer.instruments.fixed_leg import FixedLegModel, FixedLeg
from pricer.instruments.floating_leg import FloatingLegModel, FloatingLeg
from pricer.utils.mappings import CALENDAR_MAP, DAY_COUNT_MAP, BUSINESS_CONVENTION_MAP
import QuantLib as ql

class SwapModel(BaseModel):
    trade_date: date
    end_date: date
    spot_lag: int = 2  # jours ouvrés
    notional: float
    fixed_rate: float
    fixed_frequency: str
    floating_frequency: str
    spread: float = 0.0
    calendar: str = "TARGET"
    
    # Dissociation complète
    fixed_day_count: str = "Actual360"
    floating_day_count: str = "Actual360"
    fixed_business_convention: str = "Following"
    floating_business_convention: str = "ModifiedFollowing"
    fixed_payment_lag: int = 0
    floating_payment_lag: int = 0

    @model_validator(mode="before")
    def check_fields(cls, values):
        if values.get("notional") <= 0:
            raise ValueError("Notional doit être strictement positif")
        return values

    @model_validator(mode="after")
    def check_dates(cls, model):
        if model.trade_date is None or model.end_date is None:
            raise ValueError("Trade date et end date doivent être définies")
        if model.end_date <= model.trade_date:
            raise ValueError("End date doit être après la trade date")
        return model


class Swap:
    """
    Swap vanilla simple : un fixed leg et un floating leg. 
    """

    # L'utilisation d'un floatingIndex de type ql.IborIndex est temporaire et sera remplacé par les données
    def __init__(self, model: SwapModel, floating_index: ql.IborIndex):
        self.model = model
        self.floating_index = floating_index

        # Calcul de la value_date (trade_date + spot_lag)
        calendar = CALENDAR_MAP[model.calendar]
        trade_ql = ql.Date(model.trade_date.day, model.trade_date.month, model.trade_date.year)
        self.value_date = calendar.advance(trade_ql, ql.Period(model.spot_lag, ql.Days))

        value_py = date(self.value_date.year(), self.value_date.month(), self.value_date.dayOfMonth())

        fixed_data = {
            "start_date": value_py,
            "end_date": model.end_date,
            "notional": model.notional,
            "payment_frequency": model.fixed_frequency,
            "fixed_rate": model.fixed_rate,
            "calendar": model.calendar,
            "day_count": model.fixed_day_count,
            "business_convention": model.fixed_business_convention,
            "payment_lag": model.fixed_payment_lag,
        }

        self.fixed_leg = FixedLeg(FixedLegModel(**fixed_data))
        self.fixed_leg.build_leg()

        floating_data = {
            "start_date": value_py,
            "end_date": model.end_date,
            "notional": model.notional,
            "payment_frequency": model.floating_frequency,
            "index_name": "EURIBOR3M",
            "spread": model.spread,
            "calendar": model.calendar,
            "day_count": model.floating_day_count,
            "business_convention": model.floating_business_convention,
            "fixing_lag": 2,
            "payment_lag": model.floating_payment_lag,
        }

        self.floating_leg = FloatingLeg(FloatingLegModel(**floating_data), index=floating_index)
        self.floating_leg.build_leg()


# -------------------- main test --------------------
def main():
    try:
        trade_date = date(2025, 1, 31)
        end_date = date(2026, 1, 31)

        todays_ql = ql.Date(trade_date.day, trade_date.month, trade_date.year)
        ql.Settings.instance().evaluationDate = todays_ql

        # Courbe plate pour l'index
        curve = ql.FlatForward(todays_ql, 0.03, ql.Actual360())
        index_handle = ql.YieldTermStructureHandle(curve)
        euribor_index = ql.Euribor3M(index_handle)

        # Swap model
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

        # Affichage des coupons
        print("Fixed leg coupons :")
        for i, c in enumerate(swap.fixed_leg.coupons, 1):
            print(f"Coupon {i}: {c} - Montant = {c.amount():.2f}")

        print("\nFloating leg coupons :")
        for i, c in enumerate(swap.floating_leg.coupons, 1):
            print(f"Coupon {i}: {c} - Montant = {c.amount():.2f}")

    except Exception as e:
        print(f"Erreur rencontrée : {e}")


if __name__ == "__main__":
    main()


