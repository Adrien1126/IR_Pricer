from datetime import date
from typing import List, Tuple, Union, Literal
import numpy as np
from scipy.interpolate import interp1d
from pydantic import BaseModel

from pricer.utils.dates import year_fraction, advance_date

class DiscountCurveModel(BaseModel):
    value_date: date
    pillars: List[Tuple[Union[str, date], float]]
    interp_method: Literal["linear", "cubic"] = "linear"
    interpolation_on: Literal["discount", "log_discount", "zero"] = "discount"
    allow_extrapolation: bool = False
    day_count: str = "Actual360"
    calendar: str = "TARGET"
    business_day_convention: str = "ModifiedFollowing"
    currency: str = "EUR"
    curve_id: str = "EUR_EONIA_DISC"

class DiscountCurve:
    def __init__(
        self,
        valuation_date: date,
        pillars: List[Tuple[date, float]],
        interpolation: str = "linear",
        interpolation_on: str = "discount",
        allow_extrapolation: bool = False,
        day_count: str = "Actual360",
    ):
        self.valuation_date = valuation_date
        self.day_count = day_count
        self.interpolation_on = interpolation_on
        self.allow_extrapolation = allow_extrapolation

        self.dates = [d for d, _ in pillars]
        self.raw_dfs = [df for _, df in pillars]
        self.times = [year_fraction(valuation_date, d, convention=day_count) for d in self.dates]

        # Transformation selon interpolation_on
        if interpolation_on == "discount":
            values = self.raw_dfs
        elif interpolation_on == "log_discount":
            values = np.log(self.raw_dfs)
        elif interpolation_on == "zero":
            values = [-np.log(df) / t if t > 0 else 0.0 for df, t in zip(self.raw_dfs, self.times)]
        else:
            raise ValueError(f"Interpolation type non supportée : {interpolation_on}")

        fill_val = "extrapolate" if allow_extrapolation else (np.nan, np.nan)
        self.interpolator = interp1d(self.times, values, kind=interpolation, fill_value=fill_val)

    def discount_factor(self, target_date: date) -> float:
        t = year_fraction(self.valuation_date, target_date, convention=self.day_count)
        val = float(self.interpolator(t))

        if self.interpolation_on == "discount":
            return val
        elif self.interpolation_on == "log_discount":
            return np.exp(val)
        elif self.interpolation_on == "zero":
            return np.exp(-val * t)

    @classmethod
    def from_model(cls, model: DiscountCurveModel) -> "DiscountCurve":
        converted_pillars = []
        for t, df in model.pillars:
            if isinstance(t, str):
                py_date = advance_date(model.value_date, t, calendar=model.calendar, convention=model.business_day_convention)
            elif isinstance(t, date):
                py_date = t
            else:
                raise ValueError(f"Type de pilier non supporté : {type(t)}")

            if df <= 0 or df > 1.5:
                raise ValueError(f"Discount factor invalide {df} à la date {py_date}")

            converted_pillars.append((py_date, df))

        dates_only = [d for d, _ in converted_pillars]
        if any(d2 <= d1 for d1, d2 in zip(dates_only, dates_only[1:])):
            raise ValueError("Les dates des piliers doivent être strictement croissantes")

        return cls(
            valuation_date=model.value_date,
            pillars=converted_pillars,
            interpolation=model.interp_method,
            interpolation_on=model.interpolation_on,
            allow_extrapolation=model.allow_extrapolation,
            day_count=model.day_count,
        )

def main():
    today = date.today()

    pillars = [
        ("0D", 1.0),
        ("6M", 0.98),
        ("1Y", 0.95),
        ("18M", 0.93),
        ("2Y", 0.90),
    ]

    model = DiscountCurveModel(
        value_date=today,
        pillars=pillars,
        interp_method="linear",
        interpolation_on="log_discount",
        allow_extrapolation=True,
        day_count="Actual360",
        calendar="TARGET",
        business_day_convention="ModifiedFollowing",
        currency="EUR",
        curve_id="EUR_EONIA_DISC"
    )

    curve = DiscountCurve.from_model(model)
    target_date = advance_date(today, "9M", calendar="TARGET")
    df = curve.discount_factor(target_date)
    print(f"[{model.curve_id}] DF({target_date}) = {df:.6f}")

if __name__ == "__main__":
    main()