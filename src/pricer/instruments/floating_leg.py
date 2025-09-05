from datetime import date
from pydantic import BaseModel, model_validator
import QuantLib as ql

from pricer.instruments.floating_coupon import FloatingCouponModel, FloatingCoupon
from pricer.instruments.leg import BaseLeg
from pricer.utils.mappings import CALENDAR_MAP, DAY_COUNT_MAP, BUSINESS_CONVENTION_MAP, PAYMENT_FREQUENCY_MAP


class FloatingLegModel(BaseModel):
    """
    Modèle Pydantic pour valider les données d'une 'leg' (jambe) à taux variable
    avant de créer la partie métier.
    """

    start_date: date  # Date de début de la jambe (ex: début du contrat)
    end_date: date  # Date de fin de la jambe (ex: fin du contrat)
    notional: float  # Montant notionnel (ex: 1 million d'euros)
    payment_frequency: str  # Fréquence des paiements (ex: "1M" = chaque mois)
    index_name: str = "EURIBOR3M"  # Nom de l'indice de référence (ex: Euribor 3 mois)
    spread: float = 0.0  # Spread ajouté au taux (ex: +0.25%)
    calendar: str = "TARGET"  # Calendrier utilisé pour ajuster les dates (jours ouvrés)
    day_count: str = "Actual360"  # Convention pour calculer la fraction d'année entre deux dates
    business_convention: str = "Following"  # Règle pour ajuster les dates non ouvrées
    fixing_lag: int = 2  # Décalage en jours entre la date de fixation du taux et la date de paiement
    payment_lag: int = 0  # Décalage en jours entre la fin de la période et la date de paiement

    @model_validator(mode="before")
    def check_fields(cls, values):
        # Vérifications avant création de l'objet

        # Le notionnel doit être strictement positif
        if n := values.get("notional"):
            if n <= 0:
                raise ValueError("Le notionnel doit être strictement positif")

        # La fréquence de paiement doit être dans la liste supportée
        if freq := values.get("payment_frequency"):
            if freq not in PAYMENT_FREQUENCY_MAP:
                raise ValueError(f"Fréquence '{freq}' non supportée")

        # Le calendrier doit être reconnu
        if cal := values.get("calendar"):
            if cal not in CALENDAR_MAP:
                raise ValueError(f"Calendrier '{cal}' non supporté")

        # Le day count doit être reconnu
        if dc := values.get("day_count"):
            if dc not in DAY_COUNT_MAP:
                raise ValueError(f"Day count '{dc}' non supporté")

        # La convention d'ajustement des dates doit être reconnue
        if conv := values.get("business_convention"):
            if conv not in BUSINESS_CONVENTION_MAP:
                raise ValueError(f"Convention '{conv}' non supportée")

        return values

    @model_validator(mode="after")
    def check_dates(cls, model):
        # Validation après création de l'objet : la date de fin doit être après la date de début
        if model.end_date <= model.start_date:
            raise ValueError("La date de fin doit être après la date de début")
        return model


class FloatingLeg(BaseLeg):
    """
    Classe représentant une jambe (leg) à taux variable.
    Elle utilise BaseLeg (qui gère les calendriers, fréquences, etc.) 
    et construit une liste de FloatingCoupon (coupons à taux variable).
    """

    def __init__(self, model: FloatingLegModel, index: ql.IborIndex):
        # On conserve le modèle et l'indice (ex: Euribor 3M)
        self.model = model
        self.index = index

        # Conversion des paramètres texte vers objets QuantLib correspondants
        calendar = CALENDAR_MAP[model.calendar]
        day_count = DAY_COUNT_MAP[model.day_count]
        business_convention = BUSINESS_CONVENTION_MAP[model.business_convention]
        payment_frequency = PAYMENT_FREQUENCY_MAP[model.payment_frequency]

        # Appel au constructeur parent pour gérer la génération du calendrier de paiements
        super().__init__(
            start_date=model.start_date,
            end_date=model.end_date,
            notional=model.notional,
            calendar=calendar,
            payment_frequency=payment_frequency,
            day_count=day_count,
            business_convention=business_convention,
            payment_lag=model.payment_lag,
        )

        # On conserve le spread et le fixing lag dans la classe
        self.spread = model.spread
        self.fixing_lag = model.fixing_lag

        # Liste qui contiendra les coupons construits
        self.coupons = []

    def build_leg(self):
        # Génération du calendrier des dates de paiement entre start et end selon la fréquence
        schedule = self.generate_schedule()

        # Pour chaque période, on crée un FloatingCoupon
        for i in range(len(schedule) - 1):
            start = schedule[i]
            end = schedule[i + 1]

            # Calcul de la date de paiement en avançant la date de fin de période selon le payment lag
            payment_date = self.calendar.advance(end, ql.Period(self.model.payment_lag, ql.Days), self.business_convention)

            # Construction du modèle FloatingCoupon pour cette période
            coupon_model = FloatingCouponModel(
                start_date=date(start.year(), start.month(), start.dayOfMonth()),
                end_date=date(end.year(), end.month(), end.dayOfMonth()),
                payment_date=date(payment_date.year(), payment_date.month(), payment_date.dayOfMonth()),
                notional=self.model.notional,
                spread=self.spread,
                index_name=self.model.index_name,
                calendar=self.model.calendar,
                day_count=self.model.day_count,
                fixing_lag=self.fixing_lag,
                convention=self.model.business_convention,
            )

            # Création du coupon FloatingCoupon à partir du modèle et de l'indice
            coupon = FloatingCoupon(coupon_model, self.index)

            # Ajout du coupon à la liste
            self.coupons.append(coupon)

        return self.coupons


# ---------- petit test / démonstration ----------
def main():
    try:
        # Initialisation QuantLib à une date donnée (31 janvier 2025)
        todays_date = ql.Date(31, 1, 2025)
        ql.Settings.instance().evaluationDate = todays_date

        # Création d'une courbe de taux plate à 3% (constante dans le temps)
        curve = ql.FlatForward(todays_date, 0.03, ql.Actual360())

        # Création d'un index Euribor 3M basé sur cette courbe
        index = ql.Euribor3M(ql.YieldTermStructureHandle(curve))

        # Définition du modèle pour la jambe à taux variable
        model = FloatingLegModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 6, 30),
            notional=1_000_000,  # 1 million d'euros
            payment_frequency="1M",  # paiements mensuels
            index_name="EURIBOR3M",
            spread=0.0025,  # +0.25% au taux de référence
            calendar="TARGET",
            day_count="Actual360",
            business_convention="ModifiedFollowing",
            fixing_lag=2,  # décalage de 2 jours pour la fixation du taux
            payment_lag=2,  # paiement 2 jours après la fin de période
        )

        # Création de la jambe à taux variable
        leg = FloatingLeg(model, index)

        # Construction de la liste des coupons (un par période)
        coupons = leg.build_leg()

        # Affichage des informations pour chaque coupon créé
        for i, coupon in enumerate(coupons, 1):
            print(f"Coupon {i}: {coupon}\n - Montant = {coupon.amount():.2f}")

    except Exception as e:
        print(f"Erreur rencontrée : {e}")


if __name__ == "__main__":
    main()
