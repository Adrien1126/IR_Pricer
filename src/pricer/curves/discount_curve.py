from datetime import date
from typing import List, Tuple, Union, Literal
import numpy as np
from scipy.interpolate import interp1d
from pydantic import BaseModel

from pricer.utils.dates import year_fraction, advance_date

# Modèle de données pour la courbe de discount,
# valide les données en entrée (date, facteurs, méthode d'interpolation, etc.)
class DiscountCurveModel(BaseModel):
    value_date: date  # Date de départ (date d'évaluation)
    pillars: List[Tuple[Union[str, date], float]]  # Liste des piliers : date + facteur d'actualisation
    interp_method: Literal["linear", "cubic"] = "linear"  # Méthode d'interpolation (linéaire ou cubique)
    interpolation_on: Literal["discount", "log_discount", "zero"] = "discount"  # Quantité sur laquelle on interpole
    allow_extrapolation: bool = False  # Autoriser extrapolation en dehors des piliers connus
    day_count: str = "Actual360"  # Convention de calcul des fractions d'années
    calendar: str = "TARGET"  # Calendrier pour ajustement jours ouvrés
    business_day_convention: str = "ModifiedFollowing"  # Règle de report des jours non ouvrés
    currency: str = "EUR"  # Devise de la courbe
    curve_id: str = "EUR_EONIA_DISC"  # Identifiant de la courbe


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
        # Date de référence pour la courbe (date d'évaluation)
        self.valuation_date = valuation_date
        # Convention utilisée pour calculer les durées en années
        self.day_count = day_count
        # Type de valeur sur laquelle on fait l'interpolation (facteur, log ou taux zéro)
        self.interpolation_on = interpolation_on
        # Autorisation ou non d'extrapoler en dehors des dates piliers
        self.allow_extrapolation = allow_extrapolation

        # Extraction des dates et des facteurs d'actualisation
        self.dates = [d for d, _ in pillars]
        self.raw_dfs = [df for _, df in pillars]

        # Calcul des durées (en années) entre la date de valeur et chaque date pilier
        self.times = [year_fraction(valuation_date, d, convention=day_count) for d in self.dates]

        # Selon le type d'interpolation choisi, on transforme les facteurs pour interpolation :
        # - interpolation sur les facteurs eux-mêmes
        # - interpolation sur les logarithmes des facteurs (utile pour interpolation plus lisse)
        # - interpolation sur les taux zéro (taux d'intérêt instantanés)
        if interpolation_on == "discount":
            values = self.raw_dfs
        elif interpolation_on == "log_discount":
            values = np.log(self.raw_dfs)
        elif interpolation_on == "zero":
            # Calcul des taux zéro à partir des facteurs
            values = [-np.log(df) / t if t > 0 else 0.0 for df, t in zip(self.raw_dfs, self.times)]
        else:
            raise ValueError(f"Interpolation type non supportée : {interpolation_on}")

        # Préparation de l'interpolateur avec la méthode choisie
        # - fill_value gère les valeurs en dehors des piliers (extrapolation ou NaN)
        fill_val = "extrapolate" if allow_extrapolation else (np.nan, np.nan)
        self.interpolator = interp1d(self.times, values, kind=interpolation, fill_value=fill_val)

    def discount_factor(self, target_date: date) -> float:
        # Calcule le facteur d'actualisation pour une date cible donnée

        # Calcul du temps (en années) entre la date d'évaluation et la date cible
        t = year_fraction(self.valuation_date, target_date, convention=self.day_count)

        # Calcul de la valeur interpolée (sur la base des transformations selon interpolation_on)
        val = float(self.interpolator(t))

        # Selon le type d'interpolation, on reconvertit la valeur pour obtenir le facteur d'actualisation
        if self.interpolation_on == "discount":
            # Valeur directement le facteur d'actualisation
            return val
        elif self.interpolation_on == "log_discount":
            # Exponentielle du logarithme pour retrouver le facteur
            return np.exp(val)
        elif self.interpolation_on == "zero":
            # Conversion depuis le taux zéro interpolé
            return np.exp(-val * t)

    @classmethod
    def from_model(cls, model: DiscountCurveModel) -> "DiscountCurve":
        # Création d'une instance DiscountCurve à partir du modèle Pydantic
        converted_pillars = []

        # Conversion des dates données en string (ex : "6M") vers des objets date Python
        for t, df in model.pillars:
            if isinstance(t, str):
                # Décalage de la date d'évaluation selon la chaîne (ex: "6M" = +6 mois)
                py_date = advance_date(model.value_date, t, calendar=model.calendar, convention=model.business_day_convention)
            elif isinstance(t, date):
                py_date = t
            else:
                raise ValueError(f"Type de pilier non supporté : {type(t)}")

            # Validation simple du facteur d'actualisation (doit être dans une plage raisonnable)
            if df <= 0 or df > 1.5:
                raise ValueError(f"Discount factor invalide {df} à la date {py_date}")

            converted_pillars.append((py_date, df))

        # Vérification que les dates sont strictement croissantes
        dates_only = [d for d, _ in converted_pillars]
        if any(d2 <= d1 for d1, d2 in zip(dates_only, dates_only[1:])):
            raise ValueError("Les dates des piliers doivent être strictement croissantes")

        # Instanciation finale
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

    # Exemple de piliers (date relative + facteur d'actualisation)
    # "0D" = aujourd'hui, facteur 1.0 (valeur actuelle)
    # "6M" = 6 mois plus tard, facteur 0.98 (1€ dans 6 mois vaut 0.98€ aujourd'hui)
    pillars = [
        ("0D", 1.0),
        ("6M", 0.98),
        ("1Y", 0.95),
        ("18M", 0.93),
        ("2Y", 0.90),
    ]

    # Construction du modèle de courbe avec ces données
    model = DiscountCurveModel(
        value_date=today,
        pillars=pillars,
        interp_method="linear",        # interpolation linéaire entre piliers
        interpolation_on="log_discount",  # interpolation sur le log des facteurs (plus stable)
        allow_extrapolation=True,      # autoriser extrapolation hors piliers
        day_count="Actual360",         # convention pour calculer le temps
        calendar="TARGET",             # calendrier de jours ouvrés
        business_day_convention="ModifiedFollowing",
        currency="EUR",
        curve_id="EUR_EONIA_DISC"
    )

    # Création de la courbe à partir du modèle
    curve = DiscountCurve.from_model(model)

    # Calcul de la date cible : aujourd'hui + 9 mois
    target_date = advance_date(today, "9M", calendar="TARGET")

    # Calcul du facteur d'actualisation à cette date
    df = curve.discount_factor(target_date)

    print(f"[{model.curve_id}] DF({target_date}) = {df:.6f}")


if __name__ == "__main__":
    main()