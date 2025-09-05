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
    spread: float = 0.0           # écart ajouté au taux indexé
    index_name: str = "EURIBOR3M" # nom de l'index de référence
    calendar: str = "TARGET"
    day_count: str = "Actual360"
    fixing_lag: int = 2           # décalage en jours avant start_date pour fixer le taux
    convention: str = "ModifiedFollowing"  # convention de jour ouvré pour ajuster la date de fixing

    @model_validator(mode="before")
    def validate_before(cls, values):
        # Notionnel doit être strictement positif
        if (n := values.get("notional")) is not None and n <= 0:
            raise ValueError("Le notionnel doit être strictement positif.")
        return values

    @model_validator(mode="after")
    def validate_after(cls, model):
        # Validation des valeurs spécifiques
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

    Le taux est soit un fixing historique (si dispo),
    soit un taux forward calculé à partir de la courbe de taux associée à l'index.
    """

    def __init__(self, model: FloatingCouponModel, index: ql.IborIndex):
        # Récupération des objets QuantLib correspondants
        calendar = CALENDAR_MAP[model.calendar]
        day_count = DAY_COUNT_MAP[model.day_count]
        convention = BUSINESS_CONVENTION_MAP[model.convention]

        # Initialisation de la classe parente (dates, notionnel, calendrier)
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

        # Calcul de la date de fixing (date à laquelle on observe le taux indexé)
        self.fixing_date = calendar.advance(
            self.start_date,
            ql.Period(-model.fixing_lag, ql.Days),
            convention
        )

        # Obtention du taux indexé (fixing historique ou forward)
        self.index_rate = self._determine_rate()

    def _determine_rate(self) -> float:
        """
        Récupère le fixing historique si disponible, sinon calcule le taux forward.
        """
        try:
            # Essayer d'obtenir le fixing historique (réel)
            return self.index.fixing(self.fixing_date)
        except Exception:
            # Si absent, calcul du taux forward via la courbe
            fwd_handle = self.index.forwardingTermStructure()
            
            ql_start = self.fixing_date
            ql_end = self.end_date if isinstance(self.end_date, ql.Date) else ql.Date(self.end_date.day, self.end_date.month, self.end_date.year)

            eval_date = ql.Settings.instance().evaluationDate
            # Si la date de fixing est avant la date d'évaluation, on la remplace par la date d'évaluation
            if ql_start < eval_date:
                ql_start = eval_date

            # Calcul du taux forward simple sur la période d’accrual
            fwd = fwd_handle.forwardRate(ql_start, ql_end, self.day_count, ql.Simple)
            return float(fwd.rate())

    def amount(self) -> float:
        """
        Calcule le montant du coupon flottant :
        Notional * (taux indexé + spread) * fraction d’année.
        """
        accrual = self.day_count.yearFraction(self.start_date, self.end_date)
        return self.notional * (self.index_rate + self.spread) * accrual

    def __repr__(self):
        return (
            f"FloatingCoupon(start={self.start_date}, end={self.end_date}, pay={self.payment_date}, "
            f"notional={self.notional}, index={self.index_name}, rate={self.index_rate:.6f}, "
            f"spread={self.spread:.6f}, fixing_date={self.fixing_date})"
        )


# ---------- Test / démonstration ----------
def main():
    try:
        # 1) Définition de la date d’évaluation (today)
        todays_date = ql.Date(31, 1, 2025)
        ql.Settings.instance().evaluationDate = todays_date

        # 2) Création d’une courbe plate à 3%
        curve = ql.FlatForward(todays_date, 0.03, ql.Actual360())
        curve_handle = ql.YieldTermStructureHandle(curve)

        # 3) Création d’un index Euribor 3M lié à la courbe
        index = ql.Euribor3M(curve_handle)

        # 4) Création du modèle avec les paramètres du coupon
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
