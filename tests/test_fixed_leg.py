import pytest
from datetime import date
from pydantic import ValidationError
from pricer.instruments.fixed_leg import FixedLegModel, FixedLeg

# -------------------- Tests du modèle FixedLegModel --------------------

def test_notional_positif():
    """Le notional doit être strictement positif"""
    with pytest.raises(ValueError, match="notionnel"):
        FixedLegModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
            notional=-1000,
            payment_frequency="1M",
            fixed_rate=0.05
        )

def test_fixed_rate_valide():
    """Le taux fixe doit être entre 0 et 1"""
    with pytest.raises(ValueError, match="taux fixe"):
        FixedLegModel(
            start_date=date(2025, 1, 1),
            end_date=date(2025, 6, 1),
            notional=1_000_000,
            payment_frequency="1M",
            fixed_rate=1.5
        )

def test_end_date_before_start_date():
    """Test que la date de fin doit être après la date de début"""
    with pytest.raises(ValidationError) as exc_info:
        FixedLegModel(
            start_date=date(2025, 6, 1),
            end_date=date(2025, 1, 1),
            notional=1_000_000,
            payment_frequency="6M",  # plus longue que la durée négative
            fixed_rate=0.05,
            calendar="TARGET",
            day_count="Actual360",
            business_convention="Following",
            payment_lag=0,
        )

    assert "date de fin doit être strictement après la date de début" in str(exc_info.value)

# -------------------- Tests de la construction FixedLeg --------------------

def test_build_fixed_leg():
    """Vérifie que la leg fixe construit correctement les coupons"""
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

    # Vérifie qu'on a au moins un coupon
    assert len(coupons) > 0

    # Vérifie que le premier coupon a le bon notional et le bon taux
    assert coupons[0].notional == 1_000_000
    assert abs(coupons[0].fixed_rate - 0.05) < 1e-10
