from datetime import date
from pydantic import BaseModel, model_validator
import QuantLib as ql
from coupons import BaseCoupon

class FixedCouponModel(BaseModel):
    """
    Modèle Pydantic pour valider les données d'un coupon fixe avant création métier.
    
    Champs principaux :
    - start_date : début de la période d'accrual (date à partir de laquelle les intérêts courent)
    - end_date : fin de la période d'accrual (date jusqu'à laquelle les intérêts sont calculés)
    - payment_date : date à laquelle le coupon est payé (date de règlement)
    - notional : montant notionnel sur lequel les intérêts sont calculés (doit être positif)
    - fixed_rate : taux fixe appliqué au coupon (ex: 0.05 pour 5%)
    - calendar : calendrier financier utilisé pour ajuster les dates (ex: TARGET)
    - day_count : convention de calcul des intérêts (ex: Actual360)
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
        # Validation basique des champs avant instanciation
        notional = values.get('notional')
        if notional is not None and notional <= 0:
            raise ValueError("Le notionnel doit être strictement positif")

        fixed_rate = values.get('fixed_rate')
        if fixed_rate is not None and not (0 <= fixed_rate <= 1):
            raise ValueError("Le taux fixe doit être entre 0 et 1 (ex: 0.05 pour 5%)")

        calendar = values.get('calendar')
        supported = ["TARGET", "UnitedStates", "NullCalendar"]
        if calendar is not None and calendar not in supported:
            raise ValueError(f"Calendrier '{calendar}' non supporté. Choisir parmi {supported}")
    
        supported_day_counts = ["Actual360", "Thirty360", "Actual365Fixed"]
        day_count = values.get('day_count')
        if day_count is not None and day_count not in supported_day_counts:
            raise ValueError(f"Day count '{day_count}' non supporté. Choisir parmi {supported_day_counts}")

        return values

    @model_validator(mode='after')
    def check_dates_consistency(cls, model):
        # Validation logique des dates une fois les champs validés
        if model.end_date <= model.start_date:
            raise ValueError("La date de fin doit être strictement après la date de début")
        if model.payment_date < model.end_date:
            raise ValueError("La date de paiement doit être après la date de fin")
        return model


class FixedCoupon(BaseCoupon):
    """
    Classe métier représentant un coupon à taux fixe.
    Hérite de BaseCoupon et ajoute le taux fixe + calcul du montant.
    """

    def __init__(self, model: FixedCouponModel):
        # Mapping du calendrier sous forme de string vers objet QuantLib Calendar
        if model.calendar == "TARGET":
            calendar = ql.TARGET()
        elif model.calendar == "UnitedStates":
            calendar = ql.UnitedStates()
        elif model.calendar == "NullCalendar":
            calendar = ql.NullCalendar()
        else:
            raise ValueError(f"Calendrier QuantLib non reconnu: {model.calendar}")

        # Mapping des conventions de calcul d'intérêt vers QuantLib DayCounter
        day_count_map = {
            "Actual360": ql.Actual360(),
            "Thirty360": ql.Thirty360(ql.Thirty360.BondBasis),
            "Actual365Fixed": ql.Actual365Fixed(),
        }
        if model.day_count not in day_count_map:
            raise ValueError(f"Day count QuantLib non reconnu: {model.day_count}")
        day_count = day_count_map[model.day_count]

        # Initialisation des dates et notionnel dans la classe mère
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
    try:
        # Exemple de création et utilisation du modèle + coupon fixe métier
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
        montant = coupon.amount()
        print(f"Montant du coupon: {montant:.2f}")

    except Exception as e:
        print(f"Erreur: {e}")


if __name__ == "__main__":
    main()
