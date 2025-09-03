from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
import QuantLib as ql
from pydantic import BaseModel, Field

# Base class métier avec QuantLib (abstraite)
class BaseCoupon(ABC):
    """
    Classe abstraite représentant un coupon financier, 
    avec gestion des dates et notionnel via QuantLib.

    Attributs principaux :
    - start_date : date de début de la période d'accrual (début du coupon)
    - end_date : date de fin de la période d'accrual (fin du coupon)
    - payment_date : date à laquelle le coupon est payé (date de règlement)
    - notional : montant notionnel sur lequel le coupon est calculé
    - calendar : calendrier financier utilisé pour ajuster les dates (ex: jours ouvrés)

    Notes importantes sur les dates :
    - start_date et end_date définissent la période pendant laquelle les intérêts courent.
    - payment_date est souvent postérieur à end_date, incluant un délai de règlement (settlement lag).
    - La trade_date (date de négociation) n'est pas gérée ici car le coupon est un composant de produit.
    - La value_date (date de valeur) est souvent la start_date ou une date proche, elle est gérée au niveau du produit.
    """

    def __init__(
        self,
        start_date: date,
        end_date: date,
        payment_date: date,
        notional: float,
        calendar: ql.Calendar = ql.TARGET(),
    ):
        # Conversion des dates Python en objets QuantLib Date
        self.start_date = ql.Date(start_date.day, start_date.month, start_date.year)
        self.end_date = ql.Date(end_date.day, end_date.month, end_date.year)
        self.payment_date = ql.Date(payment_date.day, payment_date.month, payment_date.year)
        self.notional = notional
        self.calendar = calendar

    @abstractmethod
    def amount(self) -> float:
        """
        Calcul du montant du coupon.
        À implémenter dans les classes filles (FixedCoupon, FloatingCoupon, etc).
        """
        pass

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(start={self.start_date}, end={self.end_date}, "
            f"pay={self.payment_date}, notional={self.notional})"
        )
