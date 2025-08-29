from datetime import date, timedelta
from pydantic import BaseModel, model_validator
import QuantLib as ql
from coupons import BaseCoupon

class FloatingCouponModel(BaseModel):
    """
    Modèle Pydantic pour valider les données d’un coupon à taux variable (floating).
    
    Champs :
    - start_date : début de la période d’accrual.
    - end_date : fin de la période d’accrual.
    - payment_date : date de paiement du coupon.
    - notional : montant notionnel (strictement positif).
    - spread : spread ajouté au taux indexé (ex: 0.0025 = 25 bps).
    - calendar : calendrier pour ajustement des dates (ex: TARGET).
    - day_count : convention de calcul d’intérêts.
    - fixing_lag : nombre de jours ouvrés avant start_date où le taux est fixé.
    - convention : règle d’ajustement des dates (following, modified following, etc.).
    """

    start_date: date
    end_date: date
    payment_date: date
    notional: float
    spread: float = 0.0  # spread en base (ex: 0.0025 pour 25 bps)
    calendar: str = "TARGET"
    day_count: str = "Actual360"
    fixing_lag: int = 2  # jours ouvrés avant le start_date
    convention: str = "ModifiedFollowing"


    @model_validator(mode='before')
    def validate_fields(cls, values):
        # Validation simple avant instanciation du modèle

        # Notional > 0
        if (n := values.get("notional")) is not None and n <= 0:
            raise ValueError("Le notionnel doit être strictement positif.")

        # Calendrier supporté
        supported_calendars = ["TARGET", "UnitedStates", "NullCalendar"]
        if (c := values.get("calendar")) not in supported_calendars:
            raise ValueError(f"Calendrier non supporté : {c}")

        # Day count supporté
        supported_day_counts = ["Actual360", "Thirty360", "Actual365Fixed"]
        if (d := values.get("day_count")) not in supported_day_counts:
            raise ValueError(f"Day count non supporté : {d}")

        # Fixing lag >= 0
        if (lag := values.get("fixing_lag")) is not None and lag < 0:
            raise ValueError("Fixing lag doit être positif ou nul.")

        # Convention supportée
        supported_conventions = ["Following", "ModifiedFollowing", "Preceding", "Unadjusted"]
        convention = values.get("convention")
        if convention is not None and convention not in supported_conventions:
            raise ValueError(f"Convention '{convention}' non supportée. Choisir parmi {supported_conventions}")

        return values


    @model_validator(mode='after')
    def validate_dates(cls, model):
        # Validation de la cohérence entre les dates
        if model.end_date <= model.start_date:
            raise ValueError("La date de fin doit être après la date de début.")
        if model.payment_date < model.end_date:
            raise ValueError("La date de paiement doit être après la date de fin.")
        return model


class FloatingCoupon(BaseCoupon):
    """
    Coupon à taux variable, dérivé de BaseCoupon.
    Intègre fixing lag, convention d’ajustement, et un taux forward simulé.
    """

    def __init__(self, model: FloatingCouponModel):
        # Conversion string -> objet QuantLib Calendar
        calendar = {
            "TARGET": ql.TARGET(),
            "UnitedStates": ql.UnitedStates(ql.UnitedStates.GovernmentBond),
            "NullCalendar": ql.NullCalendar(),
        }[model.calendar]

        # Conversion string -> objet QuantLib DayCounter
        day_count = {
            "Actual360": ql.Actual360(),
            "Thirty360": ql.Thirty360(ql.Thirty360.BondBasis),
            "Actual365Fixed": ql.Actual365Fixed(),
        }[model.day_count]

        # Initialisation des dates et notionnel via BaseCoupon
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

        # Conversion convention string -> QuantLib BusinessDayConvention
        convention = {
            "Following": ql.Following,
            "ModifiedFollowing": ql.ModifiedFollowing,
            "Preceding": ql.Preceding,
            "Unadjusted": ql.Unadjusted,
        }[model.convention]

        # Calcul de la date de fixing en reculant de fixing_lag jours ouvrés
        # selon la convention d’ajustement (ex: Modified Following)
        self.fixing_date = calendar.advance(
            ql.Date.from_date(model.start_date),
            ql.Period(-model.fixing_lag, ql.Days),
            convention
        )

        # Simulation du taux forward (ici valeur mockée, à remplacer plus tard)
        self.index_rate = self._mock_forward_rate()

    def _mock_forward_rate(self) -> float:
        """
        Taux forward simulé.
        À remplacer par la vraie récupération du taux à fixing_date.
        """
        return 0.031  # ex: 3.1 %

    def amount(self) -> float:
        """
        Calcul du montant du coupon flottant :
        Notional * (taux forward + spread) * fraction d'année selon day_count.
        """
        accrual = self.day_count.yearFraction(self.start_date, self.end_date)
        return self.notional * (self.index_rate + self.spread) * accrual

    def __repr__(self):
        return (
            f"FloatingCoupon(start={self.start_date}, end={self.end_date}, pay={self.payment_date}, "
            f"notional={self.notional}, rate={self.index_rate:.4f}, spread={self.spread:.4f}, "
            f"fixing_date={self.fixing_date})"
        )


def main():
    try:
        model = FloatingCouponModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 7, 1),
            payment_date=date(2025, 7, 3),
            notional=1_000_000,
            spread=0.0025,  # 25 bps
            calendar="TARGET",
            day_count="Actual360",
            fixing_lag=2, 
            convention="ModifiedFollowing"
        )

        coupon = FloatingCoupon(model)

        print(coupon)
        print(f"Montant du coupon : {coupon.amount():.2f} EUR")

    except Exception as e:
        print(f"Erreur lors de la création du FloatingCoupon : {e}")

if __name__ == "__main__":
    main()
