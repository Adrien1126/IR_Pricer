import pytest
import QuantLib as ql
from datetime import date

from pricer.instruments.floating_leg import FloatingLegModel, FloatingLeg


@pytest.fixture
def flat_curve_index():
    """Retourne un index EURIBOR3M avec une courbe plate à 3%."""
    eval_date = ql.Date(31, 1, 2025)
    ql.Settings.instance().evaluationDate = eval_date
    curve = ql.FlatForward(eval_date, 0.03, ql.Actual360())
    return ql.Euribor3M(ql.YieldTermStructureHandle(curve))

def get_flat_curve(rate=0.03):
    eval_date = ql.Date(31, 1, 2025)
    ql.Settings.instance().evaluationDate = eval_date
    curve = ql.FlatForward(eval_date, rate, ql.Actual360())
    return ql.YieldTermStructureHandle(curve)

@pytest.fixture
def floating_leg_model():
    """Modèle simple d'une FloatingLeg avec paiements mensuels."""
    return FloatingLegModel(
        start_date=date(2025, 1, 31),
        end_date=date(2025, 6, 30),
        notional=1_000_000,
        payment_frequency="1M",
        index_name="EURIBOR3M",
        spread=0.0025,
        calendar="TARGET",
        day_count="Actual360",
        business_convention="ModifiedFollowing",
        fixing_lag=2,
        payment_lag=2,
    )

"""
Le test ne passe pas car les courbes QuantLib crée un écart bien que ce soit une flatCurve, 
à étudier lorsque nos courbes seront définis
"""

def test_floating_leg_creation(floating_leg_model, flat_curve_index):
    leg = FloatingLeg(floating_leg_model, flat_curve_index)
    coupons = leg.build_leg()

    assert len(coupons) == 5  # Janvier à Juin

    for coupon in coupons:
        assert coupon.notional == floating_leg_model.notional
        assert coupon.index_rate == pytest.approx(0.03, abs=1e-4)
        assert coupon.spread == 0.0025
        assert coupon.amount() > 0



def test_floating_leg_coupon_dates_are_ordered(floating_leg_model, flat_curve_index):
    leg = FloatingLeg(floating_leg_model, flat_curve_index)
    coupons = leg.build_leg()

    for i in range(len(coupons) - 1):
        assert coupons[i].end_date <= coupons[i + 1].start_date
