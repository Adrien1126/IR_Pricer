# src/pricer/instruments/fixed_coupon.py

from datetime import date
from pydantic import BaseModel, model_validator
import QuantLib as ql
from pricer.instruments.coupon import BaseCoupon
from pricer.utils.mappings import CALENDAR_MAP, DAY_COUNT_MAP

class FixedCouponModel(BaseModel):
    """
    Modèle Pydantic pour valider les données d'un coupon fixe avant création métier.
    """

    start_date: date
    end_date: date
    payment_date: date
    notional: float
    fixed_rate: float
    calendar: str = "TARGET"
    day_count: str = "Actual360"

    @model_validator(mode='before')
    def check_fields(cls, values):
        # Validation basique des champs
        notional = values.get('notional')
        if notional is not None and notional <= 0:
            raise ValueError("Le notionnel doit être strictement positif")

        fixed_rate = values.get('fixed_rate')
        if fixed_rate is not None and not (0 <= fixed_rate <= 1):
            raise ValueError("Le taux fixe doit être entre 0 et 1 (ex: 0.05 pour 5%)")

        calendar = values.get('calendar')
        if calendar is not None and calendar not in CALENDAR_MAP.keys():
            raise ValueError(f"Calendrier '{calendar}' non supporté. Choisir parmi {list(CALENDAR_MAP.keys())}")

        day_count = values.get('day_count')
        if day_count is not None and day_count not in DAY_COUNT_MAP.keys():
            raise ValueError(f"Day count '{day_count}' non supporté. Choisir parmi {list(DAY_COUNT_MAP.keys())}")

        return values

    @model_validator(mode='after')
    def check_dates_consistency(cls, model):
        if model.end_date <= model.start_date:
            raise ValueError("La date de fin doit être strictement après la date de début")
        if model.payment_date < model.end_date:
            raise ValueError("La date de paiement doit être après la date de fin")
        return model


class FixedCoupon(BaseCoupon):
    """
    Coupon à taux fixe. Hérite de BaseCoupon et ajoute le taux fixe + calcul du montant.
    """

    def __init__(self, model: FixedCouponModel):
        # Calendrier
        calendar = CALENDAR_MAP[model.calendar]

        # Day count
        day_count = DAY_COUNT_MAP[model.day_count]

        # Init parent
        super().__init__(
            start_date=model.start_date,
            end_date=model.end_date,
            payment_date=model.payment_date,
            notional=model.notional,
            calendar=calendar,
        )

        self.fixed_rate = model.fixed_rate
        self.day_count = day_count

    def amount(self) -> float:
        """
        Calcul du montant du coupon fixe :
        Montant = Notional * taux fixe * fraction d'année selon la convention day count.
        """
        accrual_fraction = self.day_count.yearFraction(self.start_date, self.end_date)
        return self.notional * self.fixed_rate * accrual_fraction

    def __repr__(self):
        return (
            f"FixedCoupon(start={self.start_date}, end={self.end_date}, pay={self.payment_date}, "
            f"notional={self.notional}, fixed_rate={self.fixed_rate}, day_count={self.day_count.name()})"
        )


def main():
    # Test rapide
    model = FixedCouponModel(
        start_date=date(2025, 1, 1),
        end_date=date(2025, 7, 1),
        payment_date=date(2025, 7, 3),
        notional=1_000_000,
        fixed_rate=0.05,
        calendar="TARGET",
        day_count="Actual360"
    )

    coupon = FixedCoupon(model)
    print(coupon)
    print(f"Montant du coupon: {coupon.amount():.2f}")


if __name__ == "__main__":
    main()
