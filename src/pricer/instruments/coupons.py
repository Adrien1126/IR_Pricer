from abc import ABC, abstractmethod
from datetime import date
from typing import Optional
import QuantLib as ql
from pydantic import BaseModel, validator, root_validator, Field

# Base class métier avec QuantLib (abstraite)
class BaseCoupon(ABC):
    def __init__(
        self,
        start_date: date,
        end_date: date,
        payment_date: date,
        notional: float,
        calendar: ql.Calendar = ql.TARGET(),
    ):
        self.start_date = ql.Date(start_date.day, start_date.month, start_date.year)
        self.end_date = ql.Date(end_date.day, end_date.month, end_date.year)
        self.payment_date = ql.Date(payment_date.day, payment_date.month, payment_date.year)
        self.notional = notional
        self.calendar = calendar

    @abstractmethod
    def amount(self) -> float:
        pass

    def __repr__(self):
        return (
            f"{self.__class__.__name__}(start={self.start_date}, end={self.end_date}, "
            f"pay={self.payment_date}, notional={self.notional})"
        )
