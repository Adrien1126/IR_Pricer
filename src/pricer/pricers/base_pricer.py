from abc import ABC, abstractmethod
from typing import Union
from pricer.instruments.fixed_coupon import FixedCoupon
from pricer.instruments.floating_coupon import FloatingCoupon
from pricer.instruments.fixed_leg import FixedLeg
from pricer.instruments.floating_leg import FloatingLeg
from pricer.instruments.swap import Swap
from pricer.curves.discount_curve import DiscountCurve

class BasePricer(ABC):
    @abstractmethod
    def price(self, instrument: Union[FixedCoupon, FloatingCoupon, FixedLeg, FloatingLeg, Swap], curve: DiscountCurve) -> float:
        """Méthode générique pour pricer un instrument financier."""
        pass
