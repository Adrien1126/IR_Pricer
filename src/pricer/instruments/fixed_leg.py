from datetime import date
from typing import List
from pydantic import BaseModel, model_validator
from dateutil.relativedelta import relativedelta
import QuantLib as ql

from pricer.instruments.fixed_coupon import FixedCouponModel, FixedCoupon
from pricer.instruments.leg import BaseLeg
from pricer.utils.mappings import CALENDAR_MAP, DAY_COUNT_MAP, BUSINESS_CONVENTION_MAP, PAYMENT_FREQUENCY_MAP


class FixedLegModel(BaseModel):
    """ 
    Modèle Pydantic pour valider les données d'une leg à taux fixe avant création métier. 
    """

    start_date: date
    end_date: date
    notional: float
    payment_frequency: str
    fixed_rate: float
    calendar: str = "TARGET"
    day_count: str = "Actual360"
    business_convention: str = "Following"
    payment_lag: int = 0

    @model_validator(mode='before')
    def check_fields(cls, values):
        notional = values.get('notional')
        if notional is not None and notional <= 0:
            raise ValueError("Le notionnel doit être strictement positif")

        fixed_rate = values.get('fixed_rate')
        if fixed_rate is not None and not (0 <= fixed_rate <= 1):
            raise ValueError("Le taux fixe doit être entre 0 et 1 (ex: 0.05 pour 5%)")

        calendar = values.get('calendar')
        if calendar not in CALENDAR_MAP:
            raise ValueError(f"Calendrier '{calendar}' non supporté. Choisir parmi {list(CALENDAR_MAP.keys())}")

        day_count = values.get('day_count')
        if day_count not in DAY_COUNT_MAP:
            raise ValueError(f"Day count '{day_count}' non supporté. Choisir parmi {list(DAY_COUNT_MAP.keys())}")

        business_convention = values.get('business_convention')
        if business_convention not in BUSINESS_CONVENTION_MAP:
            raise ValueError(f"Business convention '{business_convention}' non supportée. Choisir parmi {list(BUSINESS_CONVENTION_MAP.keys())}")

        payment_frequency = values.get('payment_frequency')
        if payment_frequency not in PAYMENT_FREQUENCY_MAP:
            raise ValueError(f"Fréquence de paiement '{payment_frequency}' non supportée. Choisir parmi {list(PAYMENT_FREQUENCY_MAP.keys())}")


        # Vérification que la fréquence de paiement n'est pas plus longue que la leg
        period = PAYMENT_FREQUENCY_MAP[payment_frequency]
        # Convertir la période en nombre de mois
        if period.units() == ql.Months:
            freq_months = period.length()
        elif period.units() == ql.Years:
            freq_months = period.length() * 12
        else:
            # Approximation si en jours ou semaines
            freq_months = period.length() / 30

        leg_months = (values['end_date'].year - values['start_date'].year) * 12 + (values['end_date'].month - values['start_date'].month)
        if freq_months > leg_months:
            raise ValueError(f"La fréquence de paiement '{payment_frequency}' ({freq_months} mois) est supérieure à la durée de la leg ({leg_months} mois)")

        return values

    @model_validator(mode='before')
    def check_dates_consistency(cls, values):
        start = values.get('start_date')
        end = values.get('end_date')
        if start and end and end <= start:
            raise ValueError("La date de fin doit être strictement après la date de début")
        return values



class FixedLeg(BaseLeg):
    """
    Jambe à taux fixe.
    Utilise BaseLeg pour le schedule et crée des FixedCoupon.
    """

    def __init__(self, model):
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

        self.fixed_rate = model.fixed_rate
        self.model = model

    def build_leg(self):
        schedule = self.generate_schedule()
        self.coupons = []

        for i in range(len(schedule) - 1):
            start = schedule[i]
            end = schedule[i + 1]
            payment_date = self.calendar.advance(end, ql.Period(self.payment_lag, ql.Days), self.business_convention)

            coupon_model = FixedCouponModel(
                start_date=date(start.year(), start.month(), start.dayOfMonth()),
                end_date=date(end.year(), end.month(), end.dayOfMonth()),
                payment_date=date(payment_date.year(), payment_date.month(), payment_date.dayOfMonth()),
                notional=self.notional,
                fixed_rate=self.fixed_rate,
                calendar=self.model.calendar,
                day_count=self.model.day_count,
            )
            coupon = FixedCoupon(coupon_model)
            self.coupons.append(coupon)

        return self.coupons

def main():
    try:
        model = FixedLegModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 6, 30),
            notional=1_000_000,
            payment_frequency="1M",
            fixed_rate=0.05,
            calendar="TARGET",
            day_count="Actual360",
            business_convention="ModifiedFollowing",
            payment_lag=0,
        )

        fixed_leg = FixedLeg(model)
        coupons = fixed_leg.build_leg()

        for i, coupon in enumerate(coupons, 1):
            montant = coupon.amount()
            print(f"Coupon {i}: {coupon}\n - Montant = {montant:.2f}")

    except Exception as e:
        print(f"Erreur rencontrée : {e}")


if __name__ == "__main__":
    main()
