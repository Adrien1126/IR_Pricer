from datetime import date, timedelta
from typing import List, Tuple
import numpy as np
from scipy.interpolate import interp1d
from pydantic import BaseModel, field_validator

from pricer.utils.dates import year_fraction

class DiscountCurveModel(BaseModel):
    value_date: date
    pillars: List[Tuple[date, float]]
    interp_method: str = "linear"
    day_count: str = "Actual360"
    calendar: str = "TARGET"
    currency: str = "EUR"

    @field_validator("pillars")
    @classmethod
    def check_pillars(cls, v):
        if not v:
            raise ValueError("La liste des piliers ne peut pas être vide")
        prev_date = None
        for d, df in v:
            if df <= 0 or df > 1.5:
                raise ValueError(f"Discount factor invalide {df} à la date {d}")
            if prev_date and d <= prev_date:
                raise ValueError("Les dates des piliers doivent être strictement croissantes")
            prev_date = d
        return v

class DiscountCurve:
    def __init__(self, as_of_date: date, pillars: List[Tuple[date, float]], interpolation: str = "linear", day_count: str = "Actual360"):
        self.as_of_date = as_of_date
        self.pillar_dates = [p[0] for p in pillars]
        self.discount_factors = [p[1] for p in pillars]
        self.day_count = day_count

        self.times = [year_fraction(as_of_date, d, convention=day_count) for d in self.pillar_dates]

        self.interpolator = interp1d(
            self.times,
            self.discount_factors,
            kind=interpolation,
            fill_value="extrapolate"
        )

    def discount_factor(self, target_date: date) -> float:
        t = year_fraction(self.as_of_date, target_date, convention=self.day_count)
        return float(self.interpolator(t))

    @classmethod
    def from_model(cls, model: DiscountCurveModel) -> "DiscountCurve":
        return cls(
            as_of_date=model.value_date,
            pillars=model.pillars,
            interpolation=model.interp_method,
            day_count=model.day_count,
        )

def main():
    # Date d'aujourd'hui
    today = date.today()

    # Création des piliers (date, discount factor)
    # Ici, on crée des piliers tous les 6 mois sur 2 ans avec des DF décroissants
    pillars = [
        (today, 1.0),
        (today + timedelta(days=180), 0.98),
        (today + timedelta(days=365), 0.95),
        (today + timedelta(days=365*1.5), 0.93),
        (today + timedelta(days=365*2), 0.90),
    ]

    # Création du modèle avec validation
    model = DiscountCurveModel(
        value_date=today,
        pillars=pillars,
        interp_method="linear",
        day_count="Actual360",
        calendar="TARGET",
        currency="EUR"
    )

    # Création de la courbe à partir du modèle
    curve = DiscountCurve.from_model(model)

    # Test sur une date cible intermédiaire
    target_date = today + timedelta(days=270)  # 9 mois plus tard
    df = curve.discount_factor(target_date)

    print(f"Discount factor au {target_date} : {df:.6f}")

if __name__ == "__main__":
    main()