from abc import ABC, abstractmethod
from datetime import date
import QuantLib as ql

class BaseLeg(ABC):
    """
    Classe abstraite représentant une jambe (Leg) d’un produit de taux.
    Sert de base à FixedLeg et FloatingLeg.

    Attributs :
    - start_date : début de la jambe (premier coupon)
    - end_date : fin de la jambe (dernier coupon)
    - notional : montant nominal utilisé pour tous les coupons
    - calendar : calendrier QuantLib utilisé pour ajuster les dates
    - payment_frequency : fréquence de paiement (ex : ql.Period("6M"))
    - day_count : convention de calcul de jours (Actual360, etc.)
    - business_convention : convention d’ajustement des dates (ex: "ModifiedFollowing")
    - payment_lag : décalage (en jours ouvrés) entre la fin de période et la date de paiement
    """

    def __init__(
        self,
        start_date: date,
        end_date: date,
        notional: float,
        calendar: ql.Calendar,
        payment_frequency: ql.Period,
        day_count: ql.DayCounter,
        business_convention: int,  # <-- Note ici un int (constante QuantLib)
        payment_lag: int = 0,
    ):
        self.start_date = ql.Date.from_date(start_date)
        self.end_date = ql.Date.from_date(end_date)
        self.notional = notional
        self.calendar = calendar
        self.payment_frequency = payment_frequency
        self.day_count = day_count
        self.business_convention = business_convention
        self.payment_lag = payment_lag

        self.coupons = []  # Liste de coupons, à générer dans les classes filles

    @abstractmethod
    def build_leg(self):
        """
        Méthode à implémenter dans les classes filles.
        Elle construit les coupons de la jambe.
        """
        pass

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(start={self.start_date}, end={self.end_date}, "
            f"notional={self.notional}, frequency={self.payment_frequency}, "
            f"payment_lag={self.payment_lag})"
        )
