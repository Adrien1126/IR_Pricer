from abc import ABC, abstractmethod
from datetime import date
from typing import List, TypeVar, Generic
import QuantLib as ql
from pricer.instruments.coupon import BaseCoupon

# Déclare une variable de type pour le coupon
T = TypeVar('T', bound=BaseCoupon)

class BaseLeg(ABC, Generic[T]):
    """
    Classe abstraite représentant une jambe (Leg) d’un produit de taux.
    Gestion centralisée de la génération du schedule.
    """
    def __init__(
        self,
        start_date: date,
        end_date: date,
        notional: float,
        calendar: ql.Calendar,
        payment_frequency: ql.Period,
        day_count: ql.DayCounter,
        business_convention: int,
        payment_lag: int = 0,
    ):
        self.start_date = ql.Date(start_date.day, start_date.month, start_date.year)
        self.end_date = ql.Date(end_date.day, end_date.month, end_date.year)

        self.notional = notional
        self.calendar = calendar
        self.payment_frequency = payment_frequency
        self.day_count = day_count
        self.business_convention = business_convention
        self.payment_lag = payment_lag

        self.coupons: List[T] = []  # Liste typée selon la sous-classe

    def generate_schedule(self) -> List[ql.Date]:
        """
        Génère le calendrier des dates de coupon/paiement selon les conventions.
        Utilise QuantLib Schedule avec la fréquence et conventions passées.
        """
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
        return [schedule[i] for i in range(len(schedule))]

    @abstractmethod
    def build_leg(self) -> List[T]:
        """
        Doit être implémentée dans les classes concrètes,
        pour construire la liste des coupons de la jambe.
        """
        pass

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(start={self.start_date}, end={self.end_date}, "
            f"notional={self.notional}, frequency={self.payment_frequency}, "
            f"payment_lag={self.payment_lag})"
        )
