import pytest
from datetime import date
from pydantic import ValidationError
from pricer.instruments.fixed_leg import FixedLegModel, FixedLeg


def test_notional_positif():
    with pytest.raises(ValueError, match="notionnel"):
        FixedLegModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
            notional=-1000,
            payment_frequency="1M",
            fixed_rate=0.05
        )


def test_fixed_rate_valide():
    with pytest.raises(ValueError, match="taux fixe"):
        FixedLegModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
            notional=1_000_000,
            payment_frequency="1M",
            fixed_rate=1.5
        )


def test_end_date_before_start_date():
    with pytest.raises(ValueError, match="date de fin doit être strictement après la date de début"):
        FixedLegModel(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 1, 1),
            notional=1_000_000,
            payment_frequency="6M",
            fixed_rate=0.05,
            calendar="TARGET",
            day_count="Actual360",
            business_convention="Following",
            payment_lag=0,
        )


def test_build_fixed_leg():
    model = FixedLegModel(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 6, 30),
        notional=1_000_000,
        payment_frequency="1M",
        fixed_rate=0.05,
        calendar="TARGET",
        day_count="Actual360",
        business_convention="ModifiedFollowing",
        payment_lag=0
    )
    leg = FixedLeg(model)
    coupons = leg.build_leg()

    assert len(coupons) > 0
    assert coupons[0].notional == 1_000_000
    assert abs(coupons[0].fixed_rate - 0.05) < 1e-10


def test_build_fixed_leg_frequence_invalide():
    with pytest.raises(ValidationError, match="Fréquence de paiement '2M' non supportée"):
        model = FixedLegModel(
            start_date=date(2025, 1, 31),
            end_date=date(2025, 6, 30),
            notional=1_000_000,
            payment_frequency="2M",  # fréquence invalide
            fixed_rate=0.05,
            calendar="TARGET",
            day_count="Actual360",
            business_convention="ModifiedFollowing",
            payment_lag=0
        )