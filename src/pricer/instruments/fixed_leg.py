from datetime import date
from pydantic import BaseModel, model_validator 
import QuantLib as ql
from leg import BaseLeg
from fixed_coupon import FixedCouponModel, FixedCoupon

class FixeLegModel(BaseModel):
    """ 
    Modèle Pydantic pour valider les données d'une leg à taux fixe avant création métier. 

    Champs principaux :
    - start_date : début de la jambe (premier coupon)
    - end_date : fin de la jambe (dernier coupon)
    - notional : montant nominal utilisé pour tous les coupons
    - calendar : calendrier QuantLib utilisé pour ajuster les dates
    - payment_frequency : fréquence de paiement (ex : "6M")
    - day_count : convention de calcul de jours (Actual360, etc.)
    - business_convention : convention d’ajustement des dates (ex: "ModifiedFollowing")
    - payment_lag : décalage (en jours ouvrés) entre la fin de période et la date de paiement
    - fixed_rate : taux fixe appliqué au coupon (ex: 0.05 pour 5%)
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
        # Validation des champs avant instanciation 
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
        return model


class FixedLeg(BaseLeg):
    """
    Classe métier représentant une leg à taux fixe.
    Hérite de BaseLeg et ajoute la gestion des coupons fixes.
    """

    def __init__(self, model: FixeLegModel):

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

        business_convention_map = {
            "Following": ql.Following,
            "ModifiedFollowing": ql.ModifiedFollowing,
            "Preceding": ql.Preceding,
        }
        if model.business_convention not in business_convention_map:
            raise ValueError(f"Business convention non reconnue: {model.business_convention}")
        business_convention = business_convention_map[model.business_convention]

        super().__init__(
            start_date=model.start_date,
            end_date=model.end_date,
            notional=model.notional,
            calendar=calendar,
            payment_frequency=model.payment_frequency,
            day_count=day_count,
            business_convention=business_convention,
            payment_lag=model.payment_lag,
        )

        self.fixed_rate = model.fixed_rate

    def build_leg(self):
        """
        Crée les coupons fixes pour la leg en fonction des paramètres définis.
        """
        coupons = []
        schedule = ql.Schedule(
            self.start_date,
            self.end_date,
            self.payment_frequency,
            self.calendar,
            self.business_convention,
            self.business_convention,
            ql.DateGeneration.Forward,
            False,
        )
        for i in range(schedule.size()):
            coupons.append(FixedCoupon(
                start_date=schedule.date(i),
                end_date=schedule.date(i + 1),
                payment_date=schedule.date(i + 2),
                notional=self.notional,
                fixed_rate=self.fixed_rate,
                calendar=self.calendar,
                day_count=self.day_count
            ))
        return coupons


def main():
    try:
        # Création du modèle avec des données d'exemple
        model = FixeLegModel(
            start_date=date(2025, 1, 1),
            end_date=date(2026, 1, 1),
            notional=1_000_000,
            payment_frequency="6M",
            fixed_rate=0.05,
            calendar="TARGET",
            day_count="Actual360",
            business_convention="Following",
            payment_lag=2,
        )

        # Création de la leg fixe métier
        fixed_leg = FixedLeg(model)

        # Génération des coupons
        coupons = fixed_leg.build_leg()

        # Affichage des coupons générés
        for i, coupon in enumerate(coupons, 1):
            montant = coupon.amount()
            print(f"Coupon {i}: {coupon} - Montant = {montant:.2f}")

    except Exception as e:
        print(f"Erreur rencontrée : {e}")

if __name__ == "__main__":
    main()