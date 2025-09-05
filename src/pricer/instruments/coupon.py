from abc import ABC, abstractmethod
from datetime import date
import QuantLib as ql

class BaseCoupon(ABC):
    """
    Classe abstraite représentant un coupon financier.
    
    Cette classe sert de modèle de base pour différents types de coupons (fixe, variable, etc).
    Elle gère les dates importantes du coupon et le montant notionnel, en utilisant QuantLib
    pour manipuler les dates financières (calendrier, jours ouvrés).

    Attributs principaux :
    - start_date : début de la période où les intérêts s'accumulent (période d'accrual)
    - end_date : fin de cette période d'accumulation
    - payment_date : date à laquelle le coupon est payé (peut être après la période d'accrual)
    - notional : montant de référence sur lequel les intérêts sont calculés
    - calendar : calendrier des jours ouvrés utilisé pour ajuster les dates (ex : TARGET)

    Remarques :
    - La classe est abstraite, ce qui signifie qu'elle ne peut pas être instanciée directement.
      Les sous-classes devront définir la méthode `amount()` pour calculer le montant du coupon.
    - La gestion des dates est faite avec QuantLib, pour assurer la conformité aux standards financiers.
    """

    def __init__(
        self,
        start_date: date,
        end_date: date,
        payment_date: date,
        notional: float,
        calendar: ql.Calendar = ql.TARGET(),
    ):
        # Convertit les dates Python standard en objets QuantLib Date
        self.start_date = ql.Date(start_date.day, start_date.month, start_date.year)
        self.end_date = ql.Date(end_date.day, end_date.month, end_date.year)
        self.payment_date = ql.Date(payment_date.day, payment_date.month, payment_date.year)
        self.notional = notional
        self.calendar = calendar

    @abstractmethod
    def amount(self) -> float:
        """
        Méthode abstraite à implémenter dans les classes filles.
        Doit retourner le montant du coupon.
        """
        pass

    def __repr__(self):
        # Représentation textuelle pour faciliter le débogage et l'affichage
        return (
            f"{self.__class__.__name__}(start={self.start_date}, end={self.end_date}, "
            f"pay={self.payment_date}, notional={self.notional})"
        )
