# src/pricer/instruments/floating_coupon.py

from datetime import date
from pydantic import BaseModel, model_validator
import QuantLib as ql

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).resolve().parents[2]))

from pricer.instruments.coupon import BaseCoupon
from pricer.utils.mappings import CALENDAR_MAP, DAY_COUNT_MAP, BUSINESS_CONVENTION_MAP


class FloatingCouponModel(BaseModel):
    """
    Modèle Pydantic pour valider les données d’un coupon à taux variable (floating).
    """

    start_date: date
    end_date: date
    payment_date: date
    notional: float
    spread: float = 0.0
    index_name: str = "EURIBOR3M"
    calendar: str = "TARGET"
    day_count: str = "Actual360"
    fixing_lag: int = 2
    convention: str = "ModifiedFollowing"

    @model_validator(mode="before")
    def validate_before(cls, values):
        if (n := values.get("notional")) is not None and n <= 0:
            raise ValueError("Le notionnel doit être strictement positif.")
        return values

    @model_validator(mode="after")
    def validate_after(cls, model):
        if model.calendar not in CALENDAR_MAP:
            raise ValueError(f"Calendrier non supporté : {model.calendar}")

        if model.day_count not in DAY_COUNT_MAP:
            raise ValueError(f"Day count non supporté : {model.day_count}")

        if model.fixing_lag < 0:
            raise ValueError("Fixing lag doit être positif ou nul.")

        if model.convention not in BUSINESS_CONVENTION_MAP:
            raise ValueError(f"Convention '{model.convention}' non supportée.")

        if model.end_date <= model.start_date:
            raise ValueError("La date de fin doit être après la date de début.")

        if model.payment_date < model.end_date:
            raise ValueError("La date de paiement doit être après la date de fin.")

        return model


class FloatingCoupon(BaseCoupon):
    """
    Coupon à taux variable.
    Peut utiliser soit un fixing historique (si disponible),
    soit une courbe forward pour simuler le taux.
    """

    def __init__(self, model: FloatingCouponModel, index: ql.IborIndex):
        calendar = CALENDAR_MAP[model.calendar]
        day_count = DAY_COUNT_MAP[model.day_count]
        convention = BUSINESS_CONVENTION_MAP[model.convention]

        # BaseCoupon attend des dates python (selon ton implémentation)
        super().__init__(
            start_date=model.start_date,
            end_date=model.end_date,
            payment_date=model.payment_date,
            notional=model.notional,
            calendar=calendar,
        )

        self.spread = model.spread
        self.day_count = day_count
        self.fixing_lag = model.fixing_lag
        self.index = index
        self.index_name = model.index_name

        # Date de fixing (QuantLib Date)
        self.fixing_date = calendar.advance(
            self.start_date,
            ql.Period(-model.fixing_lag, ql.Days),
            convention
        )

        # Détermination du taux (fixing si dispo, sinon forward curve)
        self.index_rate = self._determine_rate()

    def _determine_rate(self) -> float:
        """
        Récupère le fixing historique si présent, sinon calcule le forward
        à partir de la courbe liée à l'index.
        """
        try:
            # tenter un fixing historique
            return self.index.fixing(self.fixing_date)
        except Exception:
            # fallback : utiliser la courbe forward
            fwd_handle = self.index.forwardingTermStructure()
            # convertir les dates Python en QuantLib Date si nécessaire
            ql_start = self.fixing_date
            ql_end = self.end_date if isinstance(self.end_date, ql.Date) else ql.Date(self.end_date.day, self.end_date.month, self.end_date.year)

            # éviter negative time : si start < evaluationDate, on prend evalDate
            eval_date = ql.Settings.instance().evaluationDate
            if ql_start < eval_date:
                ql_start = eval_date

            # forwardRate(start, end, dayCounter, compounding)
            fwd = fwd_handle.forwardRate(ql_start, ql_end, self.day_count, ql.Simple)
            return float(fwd.rate())

    def amount(self) -> float:
        """Notional * (index + spread) * accrual_fraction"""
        accrual = self.day_count.yearFraction(self.start_date, self.end_date)
        return self.notional * (self.index_rate + self.spread) * accrual

    def __repr__(self):
        return (
            f"FloatingCoupon(start={self.start_date}, end={self.end_date}, pay={self.payment_date}, "
            f"notional={self.notional}, index={self.index_name}, rate={self.index_rate:.6f}, "
            f"spread={self.spread:.6f}, fixing_date={self.fixing_date})"
        )


# ---------- petit test / démonstration ----------
def main():
    try:
        # 1) Setup QuantLib evaluation date
        todays_date = ql.Date(31, 1, 2025)
        ql.Settings.instance().evaluationDate = todays_date

        # 2) Courbe plate 3% et Handle
        curve = ql.FlatForward(todays_date, 0.03, ql.Actual360())
        curve_handle = ql.YieldTermStructureHandle(curve)

        # 3) Index Euribor3M lié à la courbe
        index = ql.Euribor3M(curve_handle)

        # Optionnel : ajouter un fixing historique si tu veux forcer l'utilisation
        # index.addFixing(ql.Date(29,1,2025), 0.031)

        # 4) Modèle
        model = FloatingCouponModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 4, 30),
            payment_date=date(2025, 5, 2),
            notional=1_000_000,
            spread=0.0025,
            index_name="EURIBOR3M",
            calendar="TARGET",
            day_count="Actual360",
            fixing_lag=2,
            convention="ModifiedFollowing"
        )

        coupon = FloatingCoupon(model, index)
        print(coupon)
        print(f"Montant du coupon : {coupon.amount():.2f} EUR")

    except Exception as e:
        print(f"Erreur : {e}")


if __name__ == "__main__":
    main()
