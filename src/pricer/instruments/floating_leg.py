from datetime import date
from typing import List
from pydantic import BaseModel, model_validator
import QuantLib as ql
from pricer.instruments.floating_coupon import FloatingCouponModel, FloatingCoupon
from pricer.instruments.leg import BaseLeg
from pricer.utils.mappings import CALENDAR_MAP, DAY_COUNT_MAP, BUSINESS_CONVENTION_MAP, PAYMENT_FREQUENCY_MAP

class FloatingLegModel(BaseModel):
    """
    Modèle Pydantic pour valider les données d'une 'leg' à taux variable
    avant de créer la partie métier.
    """
    start_date: date
    end_date: date
    notional: float
    payment_frequency: str
    index_name: str = "EURIBOR3M"
    spread: float = 0.0
    calendar: str = "TARGET"
    day_count: str = "Actual360"
    business_convention: str = "Following"
    fixing_lag: int = 2
    payment_lag: int = 0

    @model_validator(mode="before")
    def check_fields(cls, values):
        if n := values.get("notional"):
            if n <= 0:
                raise ValueError("Le notionnel doit être strictement positif")
        if freq := values.get("payment_frequency"):
            if freq not in PAYMENT_FREQUENCY_MAP:
                raise ValueError(f"Fréquence '{freq}' non supportée")
        if cal := values.get("calendar"):
            if cal not in CALENDAR_MAP:
                raise ValueError(f"Calendrier '{cal}' non supporté")
        if dc := values.get("day_count"):
            if dc not in DAY_COUNT_MAP:
                raise ValueError(f"Day count '{dc}' non supporté")
        if conv := values.get("business_convention"):
            if conv not in BUSINESS_CONVENTION_MAP:
                raise ValueError(f"Convention '{conv}' non supportée")
        return values

    @model_validator(mode="after")
    def check_dates(cls, model):
        if model.end_date <= model.start_date:
            raise ValueError("La date de fin doit être après la date de début")
        return model

class FloatingLeg(BaseLeg[FloatingCoupon]):
    """
    Classe représentant une jambe (leg) à taux variable.
    Elle hérite de BaseLeg[FloatingCoupon] pour garantir le typage correct.
    """
    def __init__(self, model: FloatingLegModel, index: ql.IborIndex):
        self.model = model
        self.index = index
        calendar = CALENDAR_MAP[model.calendar]
        day_count = DAY_COUNT_MAP[model.day_count]
        business_convention = BUSINESS_CONVENTION_MAP[model.business_convention]
        payment_frequency = PAYMENT_FREQUENCY_MAP[model.payment_frequency]

        super().__init__(
            start_date=model.start_date,
            end_date=model.end_date,
            notional=model.notional,
            calendar=calendar,
            payment_frequency=payment_frequency,
            day_count=day_count,
            business_convention=business_convention,
            payment_lag=model.payment_lag,
        )
        self.spread = model.spread
        self.fixing_lag = model.fixing_lag

    def build_leg(self) -> List[FloatingCoupon]:
        schedule = self.generate_schedule()
        self.coupons = []

        for i in range(len(schedule) - 1):
            start = schedule[i]
            end = schedule[i + 1]
            payment_date = self.calendar.advance(end, ql.Period(self.model.payment_lag, ql.Days), self.business_convention)

            coupon_model = FloatingCouponModel(
                start_date=date(start.year(), start.month(), start.dayOfMonth()),
                end_date=date(end.year(), end.month(), end.dayOfMonth()),
                payment_date=date(payment_date.year(), payment_date.month(), payment_date.dayOfMonth()),
                notional=self.model.notional,
                spread=self.spread,
                index_name=self.model.index_name,
                calendar=self.model.calendar,
                day_count=self.model.day_count,
                fixing_lag=self.fixing_lag,
                convention=self.model.business_convention,
            )
            coupon = FloatingCoupon(coupon_model, self.index)
            self.coupons.append(coupon)

        return self.coupons


def main():
    try:
        todays_date = ql.Date(31, 1, 2025)
        ql.Settings.instance().evaluationDate = todays_date
        curve = ql.FlatForward(todays_date, 0.03, ql.Actual360())
        index = ql.Euribor3M(ql.YieldTermStructureHandle(curve))

        model = FloatingLegModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 6, 30),
            notional=1_000_000,
            payment_frequency="1M",
            index_name="EURIBOR3M",
            spread=0.0025,
            calendar="TARGET",
            day_count="Actual360",
            business_convention="ModifiedFollowing",
            fixing_lag=2,
            payment_lag=2,
        )

        leg = FloatingLeg(model, index)
        coupons = leg.build_leg()

        for i, coupon in enumerate(coupons, 1):
            print(f"Coupon {i}: {coupon}\n - Montant = {coupon.amount():.2f}")

    except Exception as e:
        print(f"Erreur rencontrée : {e}")

if __name__ == "__main__":
    main()
